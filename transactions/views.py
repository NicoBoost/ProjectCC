from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction
from marketplace.models import Publication
from .services import finalize_atomic_transaction

@login_required
def start_transaction(request, publication_id):
    """
    Simula el inicio de un servicio: crea el registro PENDIENTE.
    """
    if request.method == 'POST':
        publication = get_object_or_404(Publication, id=publication_id)
        
        # El solicitante es el usuario logueado
        solicitante = request.user 
        oferente = publication.user

        # Evitar auto-transacciones
        if solicitante == oferente:
            messages.error(request, "No puedes iniciar una transacción contigo mismo.")
            return redirect('index')

        # Crear la Transacción en estado PENDIENTE
        new_transaction = Transaction.objects.create(
            solicitante=solicitante,
            oferente=oferente,
            publication=publication,
            monto_cr=1,
            estado='PENDIENTE'
        )

        messages.info(request, f"Intercambio iniciado. Confirma la finalización para transferir 1 CR.")
        
        # Redirigir a una página de 'Mis Transacciones' o al inicio.
        return redirect('index')
    
    # Si no es POST, redirigir
    return redirect('index')


@login_required
def finalize_transaction(request, transaction_id):
    """
    Finaliza el servicio y ejecuta la Transferencia Atómica de CR (RF-02).
    Solo el OFERENTE puede confirmar el servicio.
    """
    if request.method == 'POST':
        try:
            # 1. Intentamos obtener la transacción pendiente
            tx = Transaction.objects.get(id=transaction_id, estado='PENDIENTE')
        except Transaction.DoesNotExist:
            messages.error(request, "Error: La transacción no existe o ya fue finalizada/cancelada.")
            return redirect('index')

        # 2. CRÍTICO: Verificar que el usuario sea el OFERENTE (quien recibe el pago)
        if request.user != tx.oferente:
            messages.error(request, "No tienes permiso para finalizar esta transacción. Solo el Oferente puede hacerlo.")
            return redirect('index')
            
        # 3. La lógica de servicio maneja el atomicidad (COMMIT/ROLLBACK)
        success, message = finalize_atomic_transaction(transaction_id)
        
        if success:
            messages.success(request, f"✅ Transacción finalizada: {message}")
        else:
            # Mensaje claro en caso de ROLLBACK (ej. saldo insuficiente)
            messages.error(request, f"❌ Fallo al finalizar (ROLLBACK): {message}")
            
        return redirect('index')
    
    return redirect('index')

@login_required
def cancel_transaction(request, transaction_id):
    """
    Permite al solicitante o al oferente cancelar una transacción pendiente.
    """
    if request.method == 'POST':
        tx = get_object_or_404(Transaction, id=transaction_id, estado='PENDIENTE')
        
        # Autorización: Solo el solicitante O el oferente pueden cancelar
        if request.user == tx.solicitante or request.user == tx.oferente:
            tx.estado = 'CANCELADO'
            tx.save()
            messages.warning(request, f"Intercambio cancelado: {tx.publication.titulo}. No se transfirió ningún CR.")
        else:
            messages.error(request, "No tienes permiso para cancelar esta transacción.")

        return redirect('index')
    return redirect('index')