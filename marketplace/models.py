from django.db import models
from django.contrib.auth.models import User # Para FK User
from profiles.models import Profile # Si necesitas acceder al perfil

class Skill(models.Model):
    # Tabla para clasificar los servicios (Ej: Plomería, Inglés, Jardinería)
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre

class Publication(models.Model):
    TIPO_CHOICES = [
        ('OFRECE', 'Ofrezco Servicio'),
        ('BUSCA', 'Busco Servicio'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicaciones')
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True)
    
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_anuncio = models.CharField(max_length=10, choices=TIPO_CHOICES)
    
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_anuncio_display()})'

    class Meta:
        ordering = ['-fecha_publicacion']