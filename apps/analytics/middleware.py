"""Ommaviy sahifalar ko'rishini maxfiylikka mos tarzda hisoblaydigan middleware."""
from apps.branches.models import Branch
from .services import is_likely_bot, record_analytics_event

IGNORED_PREFIXES = (
    "/boshqaruv/",
    "/admin/",
    "/static/",
    "/media/",
    "/api/",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/healthz/",
)


class PrivacyFriendlyPageViewMiddleware:
    """Ommaviy HTML sahifalarga kirishlarni PII saqlamasdan qayd etadi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method == "GET"
            and response.status_code == 200
            and not any(request.path.startswith(p) for p in IGNORED_PREFIXES)
            and "/xarita/" not in request.path
            and "text/html" in response.get("Content-Type", "")
            and not is_likely_bot(request.META.get("HTTP_USER_AGENT", ""))
        ):
            branch = None
            if request.path.startswith("/filiallar/"):
                parts = [p for p in request.path.split("/") if p]
                if len(parts) == 2:
                    branch = Branch.objects.filter(slug=parts[1], is_active=True).first()

            record_analytics_event(
                request,
                event_type="page_view",
                branch=branch,
                platform="website",
                page_path=request.path,
            )

        return response
