from django.contrib import admin
# Importamos el modelo User base de Django
from django.contrib.auth.models import User 
# Importamos la clase base de administración de usuarios
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile # Importamos nuestro modelo Profile

# 1. Definir el Perfil como un componente incrustado (Inline)
class ProfileInline(admin.StackedInline):
    model = Profile
    # Esto evita que se pueda borrar el Perfil sin borrar el Usuario
    can_delete = False 
    verbose_name_plural = 'Datos de Geolocalización y CR'
    
    # CRÍTICO: Listar los campos que deben aparecer
    fields = ('saldo_cr', 'comuna', 'coordenada_lat', 'coordenada_lon')

# 2. Definir una clase de Administración de Usuario personalizada
class CustomUserAdmin(BaseUserAdmin):
    # CRÍTICO: Añadir el Inline a la configuración del usuario
    inlines = (ProfileInline,) 
    
    # También podemos añadir el ProfileInline a los fieldsets si es necesario, pero inlines es más directo.

# 3. Desregistrar y Registrar
# Desregistramos el modelo User por defecto
admin.site.unregister(User)

# Registramos el modelo User usando nuestra clase CustomUserAdmin
admin.site.register(User, CustomUserAdmin) 

# Si quieres que el modelo Profile también sea accesible directamente en el Admin
admin.site.register(Profile)