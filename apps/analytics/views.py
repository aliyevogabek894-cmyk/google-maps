"""CTA tugmalari bosilishini qayd etuvchi CSRF-himoyalangan endpoint."""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.branches.models import Branch
from apps.core.security import check_rate_limit, get_client_ip_hash
from .services import record_analytics_event


@require_POST
def track_cta_view(request):
    """Sayt ichidagi CTA tugmalari bosilishini (masalan, 'Qabulga ariza') yozadi."""
    ip_hash = get_client_ip_hash(request)
    allowed, _ = check_rate_limit(scope="cta_track", identifier=ip_hash, limit=40, window_seconds=300)
    if not allowed:
        return JsonResponse({"ok": False, "error": "rate_limited"}, status=429)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        payload = request.POST

    cta_label = str(payload.get("cta_label", "")).strip()[:120]
    page_path = str(payload.get("page_path", "/")).strip()[:255]
    if not page_path.startswith("/"):
        page_path = "/"

    branch = None
    branch_id = payload.get("branch_id")
    if branch_id:
        try:
            branch = Branch.objects.filter(pk=int(branch_id), is_active=True).first()
        except (ValueError, TypeError):
            branch = None

    if not cta_label:
        return JsonResponse({"ok": False, "error": "missing_label"}, status=400)

    record_analytics_event(
        request,
        event_type="cta_click",
        branch=branch,
        platform="website",
        cta_label=cta_label,
        page_path=page_path,
    )
    return JsonResponse({"ok": True})
