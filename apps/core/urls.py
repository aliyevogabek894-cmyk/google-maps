from django.urls import path

from .views import about_view, contact_view, home_view, privacy_policy_view, robots_txt_view

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),
    path("maktab-haqida/", about_view, name="about"),
    path("aloqa/", contact_view, name="contact"),
    path("maxfiylik-siyosati/", privacy_policy_view, name="privacy"),
    path("robots.txt", robots_txt_view, name="robots_txt"),
]
