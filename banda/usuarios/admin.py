from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    # Esto hará que veamos el campo 'rol' y 'creado_por' en el panel de Django
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('rol', 'creado_por')}),
    )
    list_display = ['username', 'email', 'rol', 'creado_por', 'is_staff']

admin.site.register(Usuario, UsuarioAdmin)