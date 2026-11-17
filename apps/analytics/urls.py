from django.urls import path

from .views import track_cta_view

app_name = "analytics"

urlpatterns = [
    path("track-cta/", track_cta_view, name="track_cta"),
]
