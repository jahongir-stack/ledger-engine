from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from .models import Hall, WeddingPackage, WeddingBooking

class WeddingBookingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="guest", password="securepass123")
        self.hall = Hall.objects.create(name="Gold", slug="gold", description="Hall", capacity=200, base_price=1000)
        self.package = WeddingPackage.objects.create(name="VIP", price=500)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.date = (timezone.localdate() + timedelta(days=10)).isoformat()
        self.payload = dict(hall=self.hall.id, package=self.package.id, date=self.date,
                            guests=90, name="Guest", phone="+998901234567")
    def test_booking_total_and_duplicate(self):
        first = self.client.post("/api/bookings/", self.payload, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(first.data["total"], "1500.00")
        second = self.client.post("/api/bookings/", self.payload, format="json")
        self.assertEqual(second.status_code, 400)
        self.assertEqual(WeddingBooking.objects.count(), 1)
    def test_cancel_releases_date(self):
        first = self.client.post("/api/bookings/", self.payload, format="json")
        self.assertEqual(self.client.post("/api/bookings/%s/cancel/" % first.data["id"]).status_code, 200)
        self.assertEqual(self.client.post("/api/bookings/", self.payload, format="json").status_code, 201)
    def test_capacity_limit(self):
        data = {**self.payload, "guests": 201}
        self.assertEqual(self.client.post("/api/bookings/", data, format="json").status_code, 400)
    def test_anonymous_cannot_book(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post("/api/bookings/", self.payload, format="json").status_code, 401)
