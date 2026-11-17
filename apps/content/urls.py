from django.urls import path

from .views import admission_view, education_view, gallery_view, news_detail_view, news_list_view

app_name = "content"

urlpatterns = [
    path("talim/", education_view, name="education"),
    path("yangiliklar/", news_list_view, name="news_list"),
    path("yangiliklar/<slug:slug>/", news_detail_view, name="news_detail"),
    path("galereya/", gallery_view, name="gallery"),
    path("qabul/", admission_view, name="admission"),
]
