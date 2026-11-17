from django.urls import path

from .views import branch_detail_view, branch_list_view, safe_map_redirect_view

app_name = "branches"

urlpatterns = [
    path("", branch_list_view, name="list"),
    path("<slug:slug>/", branch_detail_view, name="detail"),
    path("<slug:slug>/xarita/<int:link_id>/", safe_map_redirect_view, name="map_redirect"),
]
