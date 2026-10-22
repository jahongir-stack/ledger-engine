from datetime import date
from decimal import Decimal
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Hall, WeddingPackage, MenuItem, GalleryImage, WeddingBooking, BlockedDate, Review
from .serializers import HallSerializer, PackageSerializer, MenuSerializer, GallerySerializer, BookingSerializer, ReviewSerializer, ContactSerializer
from .notifications import send_booking_alert

class Register(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = request.data.get("password", "")
        email = str(request.data.get("email", "")).strip()
        if len(username) < 3 or len(password) < 8:
            return Response({"detail": "Username >=3 and password >=8 characters required."}, status=400)
        if get_user_model().objects.filter(username=username).exists():
            return Response({"detail": "Username already exists."}, status=400)
        user = get_user_model().objects.create_user(username=username, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username}, status=201)

class Login(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
        if not user:
            return Response({"detail": "Invalid credentials."}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username, "is_staff": user.is_staff})

class Logout(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"username": request.user.username, "email": request.user.email, "is_staff": request.user.is_staff})

class HallViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hall.objects.filter(active=True)
    serializer_class = HallSerializer
    permission_classes = [AllowAny]

class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeddingPackage.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]

class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GalleryImage.objects.select_related("hall")
    serializer_class = GallerySerializer
    permission_classes = [AllowAny]

class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.filter(approved=True).select_related("customer")
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

class BookingViewSet(viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = WeddingBooking.objects.select_related("hall", "package").prefetch_related("menu_items")
        return qs if self.request.user.is_staff else qs.filter(customer=self.request.user)
    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)
    def retrieve(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        transaction.on_commit(lambda: send_booking_alert("New wedding booking #" + str(booking.id)))
        return Response(self.get_serializer(booking).data, status=201)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in ["pending", "approved"] or booking.date < date.today():
            return Response({"detail": "Cannot cancel this booking."}, status=400)
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        return Response({"status": "cancelled"})
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def decide(self, request, pk=None):
        booking = self.get_object()
        decision = request.data.get("status")
        if decision not in ["approved", "rejected"] or booking.status != "pending":
            return Response({"detail": "Only pending bookings can be approved/rejected."}, status=400)
        booking.status = decision
        booking.save(update_fields=["status"])
        return Response({"status": decision})

@api_view(["GET"])
@permission_classes([AllowAny])
def calendar(request):
    hall_id = request.query_params.get("hall")
    month = request.query_params.get("month", timezone.localdate().strftime("%Y-%m"))
    try:
        year, mon = map(int, month.split("-"))
        date(year, mon, 1)
        if not Hall.objects.filter(id=hall_id, active=True).exists():
            return Response({"detail": "Unknown hall."}, status=404)
    except (ValueError, TypeError):
        return Response({"detail": "Use valid hall and YYYY-MM month."}, status=400)
    dates = WeddingBooking.objects.filter(hall_id=hall_id, date__year=year, date__month=mon,
                                          status__in=["pending", "approved"]).values_list("date", flat=True)
    blocked = BlockedDate.objects.filter(hall_id=hall_id, date__year=year, date__month=mon).values_list("date", flat=True)
    return Response({"unavailable": sorted(set([d.isoformat() for d in dates] + [d.isoformat() for d in blocked]))})

class Contact(generics.CreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]

@api_view(["GET"])
@permission_classes([IsAdminUser])
def stats(request):
    qs = WeddingBooking.objects.filter(status="approved")
    month = timezone.localdate().replace(day=1)
    return Response({"halls": Hall.objects.count(), "bookings": WeddingBooking.objects.count(),
                     "pending": WeddingBooking.objects.filter(status="pending").count(),
                     "monthly_revenue_estimate": str(qs.filter(date__gte=month).aggregate(s=Sum("total"))["s"] or Decimal("0")),
                     "approved": qs.count()})
