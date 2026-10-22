from django.contrib import admin
from .models import Hall, WeddingPackage, MenuItem, GalleryImage, BlockedDate, WeddingBooking, Review, ContactMessage

@admin.register(WeddingBooking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hall", "date", "guests", "total", "status")
    list_filter = ("status", "hall", "date")
    search_fields = ("name", "phone", "customer__username")
    readonly_fields = ("total", "created_at")
    filter_horizontal = ("menu_items",)

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "base_price", "active")
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(WeddingPackage)
admin.site.register(MenuItem)
admin.site.register(GalleryImage)
admin.site.register(BlockedDate)
admin.site.register(Review)
admin.site.register(ContactMessage)
admin.site.site_header = "Royal Wedding Palace | Administration"
