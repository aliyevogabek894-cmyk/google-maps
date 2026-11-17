from django.urls import path

from .views import it_academy_view

app_name = "it_academy"

urlpatterns = [
    path("", it_academy_view, name="index"),
]
