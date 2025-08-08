"""
Objetivo:
- Modificar el comportamiento de funciones (como vistas) usando decoradores.

Cómo funciona:
- @group_required('Administrador') es un decorador que se pone encima de una vista.
- Al ejecutarse la vista, este decorador verifica si el usuario está en el grupo adecuado.
- Si no está autenticado, lo redirige al login.
- Si está autenticado pero no tiene el grupo, retorna un HttpResponseForbidden
"""
from django.http import HttpResponseForbidden
from functools import wraps

# Decorador para verificar roles
def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                from django.conf import settings
                from django.shortcuts import redirect
                return redirect(settings.LOGIN_URL) 
            if user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator

admin_required = group_required('Administrador')
technician_equired = group_required('Técnico')
building_equired = group_required('Cliente')