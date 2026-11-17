from django.urls import path

from .views import reviews_page_view

app_name = "reviews"

urlpatterns = [
    path("", reviews_page_view, name="list"),
]
