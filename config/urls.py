"""Turon Odob-Ilm Raqamli Maktab Platformasi — Asosiy URL marshrutlari."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import BranchSitemap, NewsSitemap, StaticPagesSitemap

admin.site.site_header = "Turon Odob-Ilm — Ma’muriyat Admini"
admin.site.site_title = "Turon Odob-Ilm Admin"
admin.site.index_title = "Tizim ma’lumotlarini boshqarish"

sitemaps = {
    "static": StaticPagesSitemap,
    "branches": BranchSitemap,
    "news": NewsSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("api/", include("apps.analytics.urls")),
    path("filiallar/", include("apps.branches.urls")),
    path("fikrlar/", include("apps.reviews.urls")),
    path("boshqaruv/", include("apps.accounts.urls")),
    path("boshqaruv/", include("apps.reports.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.core.urls")),
]

handler403 = "apps.core.views.custom_403_view"
handler404 = "apps.core.views.custom_404_view"
handler500 = "apps.core.views.custom_500_view"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
