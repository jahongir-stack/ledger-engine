from django.core.management.base import BaseCommand
from core.models import Hall, WeddingPackage, MenuItem, GalleryImage

class Command(BaseCommand):
    help = "Add idempotent demo venues, packages, menu and photos"
    def handle(self, *args, **kwargs):
        halls = [
            ("royal-gold", "Royal Gold Hall", 700, 25000000,
             "A grand ballroom with chandeliers and spectacular ceremony stage.",
             "https://images.unsplash.com/photo-1519741497674-611481863552?w=1400"),
            ("diamond", "Diamond Hall", 450, 18000000,
             "An intimate contemporary space with panoramic lights.",
             "https://images.unsplash.com/photo-1519225421980-715cb0215aed?w=1400"),
            ("imperial", "Imperial Garden", 900, 35000000,
             "Majestic celebrations surrounded by elegant gardens.",
             "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1400"),
        ]
        for slug, name, capacity, price, description, photo in halls:
            hall, _ = Hall.objects.update_or_create(slug=slug, defaults=dict(name=name, capacity=capacity,
                base_price=price, description=description, image_url=photo, active=True))
            GalleryImage.objects.get_or_create(hall=hall, url=photo, defaults={"caption": name})
        for name, price, desc in [("Standard", 0, "Essential event coordination"),
                                 ("Premium", 5500000, "Enhanced floral arrangements and DJ"),
                                 ("Gold", 12000000, "Premium decoration and live music"),
                                 ("VIP", 25000000, "Full white-glove celebration service")]:
            WeddingPackage.objects.update_or_create(name=name, defaults={"price": price, "description": desc})
        for name, cat, price in [("Osh", "Main", 45000), ("Wedding salad", "Starter", 18000),
                                 ("Fruit plate", "Dessert", 20000), ("Juice", "Drinks", 8000)]:
            MenuItem.objects.update_or_create(name=name, defaults={"category": cat, "price_per_guest": price})
        self.stdout.write(self.style.SUCCESS("Royal Wedding demo content ready."))
