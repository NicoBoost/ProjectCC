from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Publication

class Transaction(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Usuario que PAGA (Solicitante)
    solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transacciones_solicitadas')
    
    # Usuario que RECIBE el pago (Oferente)
    oferente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transacciones_ofrecidas')
    
    publication = models.ForeignKey(Publication, on_delete=models.SET_NULL, null=True)
    monto_cr = models.IntegerField(default=1) # Siempre 1 CR en el MVP
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Transacción {self.id} ({self.estado})'