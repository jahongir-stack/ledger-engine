from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

class Hall(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image_url = models.URLField(blank=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class WeddingPackage(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self): return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, default="Main")
    price_per_guest = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return self.name

class GalleryImage(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="images")
    url = models.URLField()
    caption = models.CharField(max_length=200, blank=True)

class BlockedDate(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="blocked_dates")
    date = models.DateField()
    reason = models.CharField(max_length=120, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["hall", "date"], name="unique_hall_blocked_date")]

class WeddingBooking(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    STATUS = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected"), (CANCELLED, "Cancelled")]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="wedding_bookings")
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT)
    package = models.ForeignKey(WeddingPackage, on_delete=models.PROTECT)
    menu_items = models.ManyToManyField(MenuItem, blank=True)
    date = models.DateField()
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["hall", "date"], condition=Q(status__in=["pending", "approved"]), name="unique_active_hall_booking")]
        ordering = ["-created_at"]

class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
