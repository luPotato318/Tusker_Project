from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """RBAC explícito para views funcionais, com superusuário como break-glass."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.perfil_acesso in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Seu perfil não possui acesso a este recurso.")
        return wrapped
    return decorator


class RoleRequiredMixin:
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_superuser and request.user.perfil_acesso not in self.allowed_roles:
            raise PermissionDenied("Seu perfil não possui acesso a este recurso.")
        return super().dispatch(request, *args, **kwargs)
