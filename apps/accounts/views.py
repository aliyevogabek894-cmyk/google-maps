"""Xodimlar portali kirish va chiqish ko'rinishlari."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.core.security import check_rate_limit, get_client_ip_hash
from .forms import StaffLoginForm
from .permissions import is_staff_portal_user
from .services import log_admin_action


def staff_login_view(request):
    """Rate limit va audit log bilan xodimlar kirish sahifasi."""
    if request.user.is_authenticated and is_staff_portal_user(request.user):
        return redirect("reports:dashboard")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    form = StaffLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        ip_hash = get_client_ip_hash(request)
        username = form.cleaned_data["username"].strip()
        password = form.cleaned_data["password"]

        allowed, retry_after = check_rate_limit(
            scope="staff_login",
            identifier=f"{ip_hash}:{username.lower()}",
            limit=5,
            window_seconds=900,
        )
        if not allowed:
            minutes = max(1, retry_after // 60)
            messages.error(
                request,
                f"Juda ko'p muvaffaqiyatsiz urinish. Iltimos, {minutes} daqiqadan so'ng qayta urinib ko'ring.",
            )
            return render(
                request,
                "reports/login.html",
                {"form": form, "next": next_url},
                status=429,
            )

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active and is_staff_portal_user(user):
            login(request, user)
            log_admin_action(
                request,
                action="user_login",
                target_model="User",
                target_id=user.pk,
                summary=f"{user.get_username()} boshqaruv paneliga kirdi",
                actor=user,
            )
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect("reports:dashboard")

        log_admin_action(
            request,
            action="login_failed",
            target_model="User",
            summary=f"Muvaffaqiyatsiz kirish urinishi: {username}",
            details={"username": username},
        )
        messages.error(request, "Login yoki parol noto'g'ri, yoxud boshqaruv paneliga ruxsatingiz yo'q.")

    return render(request, "reports/login.html", {"form": form, "next": next_url})


@require_POST
def staff_logout_view(request):
    """Xodimni xavfsiz tarzda tizimdan chiqaradi."""
    if request.user.is_authenticated:
        log_admin_action(
            request,
            action="user_logout",
            target_model="User",
            target_id=request.user.pk,
            summary=f"{request.user.get_username()} boshqaruv panelidan chiqdi",
        )
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect("core:home")
