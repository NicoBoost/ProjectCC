from django.db import transaction, IntegrityError
from profiles.models import Profile
from .models import Transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Esta función implementa el flujo atómico (COMMIT o ROLLBACK)
# que diseñaste en tu Diagrama de Actividad.

@transaction.atomic
def transferir_credito(solicitante_id, oferente_id, monto=1):
    """
    Realiza la transferencia atómica de Créditos de Tiempo (CR).
    Si Solicitante no tiene saldo, la BD rechaza la resta (IntegrityError)
    y se fuerza un ROLLBACK de todas las operaciones.
    """
    try:
        # 1. Obtener los perfiles (Bloquea las filas de saldo en la BD)
        solicitante_profile = Profile.objects.select_for_update().get(user__id=solicitante_id)
        oferente_profile = Profile.objects.select_for_update().get(user__id=oferente_id)
        
        # 2. Verificar saldo (aunque el constraint lo haría)
        if solicitante_profile.saldo_cr < monto:
            # Lanza un error específico que puede ser capturado
            raise ValueError("Saldo CR insuficiente para la transacción.")
        
        # 3. Restar al solicitante (PAGO)
        solicitante_profile.saldo_cr -= monto
        solicitante_profile.save() # La DB aplica el constraint >= 0
        
        # 4. Sumar al oferente (RECEPCIÓN)
        oferente_profile.saldo_cr += monto
        oferente_profile.save()
        
        # Si se llega aquí, se ejecuta el COMMIT de Django.
        return True, "Transacción atómica completada con éxito."
        
    except IntegrityError:
        # Captura errores de la DB (Ej: Saldo negativo si falló el constraint)
        # El rollback ya ocurrió automáticamente.
        return False, "Error de integridad de datos (ROLLBACK): Intento de saldo negativo."
    except ValueError as e:
        # Captura el error de saldo insuficiente
        return False, str(e)
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

# Nota: Esta función debe ser llamada desde la vista (View) de Django
# que maneja el botón 'Finalizar y Pagar 1 CR'.


@transaction.atomic
def finalize_atomic_transaction(transaction_id):
    """
    Implementa la Transferencia Atómica de Créditos (RF-02).
    Si hay algún error (ej. saldo negativo), se fuerza un ROLLBACK.
    """
    try:
        tx = Transaction.objects.select_for_update().get(id=transaction_id, estado='PENDIENTE')
        monto = tx.monto_cr
        
        # Obtener perfiles para bloquear sus saldos
        solicitante_profile = Profile.objects.select_for_update().get(user=tx.solicitante)
        oferente_profile = Profile.objects.select_for_update().get(user=tx.oferente)
        
        # 1. Verificar saldo (Critico)
        if solicitante_profile.saldo_cr < monto:
            raise ValueError("Saldo CR insuficiente.")
            
        # 2. Pagar (Resta al Solicitante)
        solicitante_profile.saldo_cr -= monto
        solicitante_profile.save()
        
        # 3. Recibir (Suma al Oferente)
        oferente_profile.saldo_cr += monto
        oferente_profile.save()
        
        # 4. Actualizar Estado (Finaliza el registro)
        tx.estado = 'FINALIZADO'
        tx.fecha_finalizacion = timezone.now()
        tx.save()
        
        # Si llegamos aquí, la transacción se confirma (COMMIT)
        return True, "Transacción completada. Se transfirieron 1 CR."

    except Transaction.DoesNotExist:
        return False, "Error: Transacción no encontrada o ya está finalizada."
    except IntegrityError:
        # El ROLLBACK ocurre automáticamente.
        logger.error("IntegrityError: Intento de saldo negativo detectado y revertido.")
        return False, "Error de integridad de datos. Transacción revertida (ROLLBACK)."
    except ValueError as e:
        # Captura el error de saldo insuficiente.
        return False, str(e)
    except Exception as e:
        return False, f"Error inesperado. Transacción revertida (ROLLBACK). Detalle: {e}"