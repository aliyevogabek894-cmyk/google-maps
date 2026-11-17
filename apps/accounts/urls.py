from django.urls import path

from .views import staff_login_view, staff_logout_view

app_name = "accounts"

urlpatterns = [
    path("kirish/", staff_login_view, name="login"),
    path("chiqish/", staff_logout_view, name="logout"),
]
