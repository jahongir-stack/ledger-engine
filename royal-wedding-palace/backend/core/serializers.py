from datetime import date
from decimal import Decimal
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import Hall, WeddingPackage, MenuItem, GalleryImage, WeddingBooking, BlockedDate, Review, ContactMessage

class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = "__all__"

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingPackage
        fields = "__all__"

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    class Meta:
        model = Review
        fields = ["id", "customer_name", "rating", "comment", "created_at"]
        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]

class BookingSerializer(serializers.ModelSerializer):
    menu_items = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, required=False)
    hall_name = serializers.CharField(source="hall.name", read_only=True)
    package_name = serializers.CharField(source="package.name", read_only=True)
    class Meta:
        model = WeddingBooking
        fields = ["id", "hall", "hall_name", "package", "package_name", "menu_items", "date", "guests",
                  "name", "phone", "notes", "total", "status", "created_at"]
        read_only_fields = ["id", "total", "status", "created_at"]

    def validate(self, attrs):
        hall = attrs["hall"]
        booked_date = attrs["date"]
        guests = attrs["guests"]
        if booked_date < date.today():
            raise serializers.ValidationError({"date": "Choose today or a future date."})
        if not hall.active or guests > hall.capacity:
            raise serializers.ValidationError({"hall": "The hall is closed or guest count exceeds capacity."})
        if BlockedDate.objects.filter(hall=hall, date=booked_date).exists():
            raise serializers.ValidationError({"date": "This date is blocked."})
        if WeddingBooking.objects.filter(hall=hall, date=booked_date, status__in=["pending", "approved"]).exists():
            raise serializers.ValidationError({"date": "Hall is already reserved on this date."})
        return attrs

    def create(self, validated_data):
        menu = validated_data.pop("menu_items", [])
        guests = validated_data["guests"]
        hall, package = validated_data["hall"], validated_data["package"]
        total = hall.base_price + package.price + sum((m.price_per_guest * guests for m in menu), Decimal("0"))
        try:
            with transaction.atomic():
                # Recheck under transaction; conditional unique constraint is authoritative.
                if BlockedDate.objects.filter(hall=hall, date=validated_data["date"]).exists():
                    raise serializers.ValidationError({"date": "Date blocked by staff."})
                booking = WeddingBooking.objects.create(customer=self.context["request"].user, total=total, **validated_data)
                booking.menu_items.set(menu)
                return booking
        except IntegrityError:
            raise serializers.ValidationError({"date": "Another customer just reserved this hall/date."})
