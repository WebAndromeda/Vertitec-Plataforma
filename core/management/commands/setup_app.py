from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from buildings.models import buildings, towers  

class Command(BaseCommand):
    help = 'Inicializa el proyecto con grupos, usuarios, edificio y torre única'

    def handle(self, *args, **kwargs):
        # Crear grupos
        for name in ['Técnico', 'Administrador', 'Cliente']:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{name}" creado'))

        # Crear usuarios con clave 'chatgpt22'
        users = [
            ('admin', 'Administrador'),
            ('tech', 'Técnico'),
            ('cliente', 'Cliente'),
        ]

        for username, groupname in users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='chatgpt22')
                user.groups.add(Group.objects.get(name=groupname))
                self.stdout.write(self.style.SUCCESS(f'Usuario "{username}" creado y asignado al grupo "{groupname}"'))

        # Crear superusuario
        if not User.objects.filter(username='root').exists():
            User.objects.create_superuser(username='root', password='chatgpt22')
            self.stdout.write(self.style.SUCCESS('Superusuario "root" creado'))

        # Crear edificio y torre única
        if not buildings.objects.exists():
            cliente = User.objects.get(username='cliente')
            building = buildings.objects.create(user=cliente, address='Dirección demo del cliente')  # ✅ Aquí el cambio
            towers.objects.create(building=building, name="Torre Única")
            self.stdout.write(self.style.SUCCESS('Edificio y Torre Única creados'))
        else:
            self.stdout.write('Ya existen edificios. No se creó uno nuevo.')
