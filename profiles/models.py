from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
#from django.db.models.signals import post_save
#from django.dispatch import receiver


# ----------------------------------------------------
# 1. Modelo de Perfil (Integra Saldo CR)
# ----------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campo CRÍTICO: Saldo de Créditos de Tiempo
    # Implementa el constraint "saldo >= 0" para forzar el ROLLBACK (RF-02)
    saldo_cr = models.IntegerField(
        default=2, # HU-01: Bono inicial de 2 CR
        validators=[MinValueValidator(0)], 
        verbose_name="Créditos de Tiempo"
    )
    
    # Campos de Geolocalización (para RF-03 futuro)
    comuna = models.CharField(max_length=50, blank=True)
    coordenada_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    coordenada_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username} (CR: {self.saldo_cr})'
    
# ----------------------------------------------------
# 2. SIGNAL (Automatización del Registro - HU-01)
# ----------------------------------------------------
#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    """Crea un Perfil al momento de crear un Usuario, asignando 2 CR."""
#    if created:
#        Profile.objects.create(user=instance)