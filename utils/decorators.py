"""
Objetivo:
- Permitir que las vistas puedan restringir el acceso a uno o varios roles (grupos) de Django.
- Reemplazar la necesidad de crear un decorador por cada grupo, haciéndolo escalable.

Cómo funciona:
- Se utiliza @roles_required('Administrador') encima de una vista.
- También soporta múltiples roles: @roles_required('Administrador', 'Técnico')
- Cuando la vista se ejecuta:
    1. Si el usuario NO está autenticado → se redirige al login.
    2. Si está autenticado pero NO pertenece a NINGUNO de los roles requeridos → retorna HttpResponseForbidden.
    3. Si pertenece a al menos un rol válido → se permite ejecutar la vista.

Ventajas:
- Evita crear decoradores repetidos como admin_required, technician_required, etc.
- Escalable: si necesitas 10 roles diferentes, este decorador los soporta todos.
- Limpio y fácil de entender en las vistas.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.conf import settings

def roles_required(*roles):
    """
    Decorador que valida si el usuario pertenece a al menos uno
    de los roles (grupos) especificados.

    Ejemplos de uso:
    @roles_required('Administrador')
    @roles_required('Administrador', 'Técnico')
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            user = request.user

            # 1. Usuario no autenticado → enviarlo al login
            if not user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            # 2. Obtener roles (grupos) del usuario
            user_roles = user.groups.values_list('name', flat=True)

            # 3. Validar si pertenece a alguno de los roles permitidos
            if any(role in user_roles for role in roles):
                return view_func(request, *args, **kwargs)

            # 4. Usuario autenticado pero sin permisos → prohibido
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

        return wrapper
    return decorator


"""
Decoradores prácticos:
- Se crean alias para no tener que escribir roles_required() a mano en cada vista.
- Estos alias NO son necesarios, pero ayudan a hacer el código más legible.
"""

admin_required = roles_required("Administrador")
technician_required = roles_required("Técnico")
building_required = roles_required("Cliente")  