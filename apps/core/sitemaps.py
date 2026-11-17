"""Dinamik XML Sitemap klasslari."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.branches.models import Branch
from apps.content.models import NewsPost


class StaticPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "core:home",
            "core:about",
            "content:education",
            "content:news_list",
            "content:gallery",
            "content:admission",
            "branches:list",
            "reviews:list",
            "core:contact",
            "core:privacy",
        ]

    def location(self, item):
        return reverse(item)


class BranchSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Branch.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class NewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return NewsPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
