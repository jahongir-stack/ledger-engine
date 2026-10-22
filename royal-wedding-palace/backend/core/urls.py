from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("halls", views.HallViewSet)
router.register("packages", views.PackageViewSet)
router.register("menu", views.MenuViewSet)
router.register("gallery", views.GalleryViewSet)
router.register("reviews", views.ReviewViewSet)
router.register("bookings", views.BookingViewSet, basename="bookings")
urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", views.Register.as_view()),
    path("auth/login/", views.Login.as_view()),
    path("auth/logout/", views.Logout.as_view()),
    path("auth/me/", views.me),
    path("calendar/", views.calendar),
    path("contact/", views.Contact.as_view()),
    path("stats/", views.stats),
]
