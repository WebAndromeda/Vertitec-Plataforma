"""
Objetivo:
- Proveer variables globales a las plantillas sin tener que pasarlas manualmente en cada render().

Cómo funciona:
- Se define una función que recibe el request y devuelve un diccionario con datos que quieras que estén disponibles en todas las plantillas.
- Por ejemplo, el context processor group_names permite usar {% if 'Administrador' in user_groups %} en cualquier plantilla.
"""

def group_names(request):
    if request.user.is_authenticated:
        groups = request.user.groups.values_list('name', flat=True)
        return {'user_groups': list(groups)}
    return {'user_groups': []}