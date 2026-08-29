from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("thank-you/<str:reference>/", views.thank_you, name="thank_you"),
]
