# /transactions/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Profile
from marketplace.models import Publication, Skill
from transactions.models import Transaction
from transactions.services import finalize_atomic_transaction # La función crítica

class AtomicTransactionTestCase(TestCase):
    """
    Casos de Prueba Críticos para la Transacción Atómica de Créditos (RF-02).
    """

    def setUp(self):
        # 1. Preparar datos base (Usuarios, Habilidad, Publicación)
        self.skill = Skill.objects.create(nombre="Clases de Python")
        
        # 2. Crear usuarios
        # UsuarioA (Solicitante/Pagador)
        self.user_a = User.objects.create_user(username='usera', password='passwordA')
        Profile.objects.create(user=self.user_a) ### NUEVO: Crear el perfil
        
        # Asignamos 5 CR para la prueba de éxito (TC-CR-001)
        self.user_a.profile.saldo_cr = 5 
        self.user_a.profile.save()

        # UsuarioB (Oferente/Receptor)
        self.user_b = User.objects.create_user(username='userb', password='passwordB')
        Profile.objects.create(user=self.user_b) ### NUEVO: Crear el perfil
        
        # Asignamos 2 CR iniciales
        self.user_b.profile.saldo_cr = 2
        self.user_b.profile.save()

        # 3. Crear una Publicación
        self.publication = Publication.objects.create(
            user=self.user_b,
            skill=self.skill,
            titulo="Clases de Django a domicilio",
            tipo_anuncio='OFRECE'
        )

        # 4. Crear una Transacción PENDIENTE
        self.transaction = Transaction.objects.create(
            solicitante=self.user_a,
            oferente=self.user_b,
            publication=self.publication,
            monto_cr=1,
            estado='PENDIENTE'
        )
        
    def test_tc_cr_001_successful_transfer(self):
        """
        Verifica el Caso de Prueba TC-CR-001: Transferencia exitosa (COMMIT).
        - A paga 1 CR, B recibe 1 CR.
        """
        # Condiciones Iniciales: Saldo A=5, Saldo B=2
        self.assertEqual(self.user_a.profile.saldo_cr, 5)
        self.assertEqual(self.user_b.profile.saldo_cr, 2)
        
        # Ejecutar la lógica atómica
        success, message = finalize_atomic_transaction(self.transaction.id)
        
        # 1. Verificar el resultado de la función
        self.assertTrue(success)
        
        # 2. Refrescar los perfiles desde la DB para obtener el saldo actualizado
        self.user_a.profile.refresh_from_db()
        self.user_b.profile.refresh_from_db()

        # 3. CRÍTICO: Verificar los saldos después del COMMIT
        self.assertEqual(self.user_a.profile.saldo_cr, 4, "El solicitante (A) debe tener 4 CR.")
        self.assertEqual(self.user_b.profile.saldo_cr, 3, "El oferente (B) debe tener 3 CR.")
        
        # 4. Verificar el estado de la Transacción
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.estado, 'FINALIZADO')

    def test_tc_cr_002_insufficient_funds_rollback(self):
        """
        Verifica el Caso de Prueba TC-CR-002: Saldo insuficiente (ROLLBACK).
        - El saldo de A (Solicitante) no cambia, el saldo de B (Oferente) tampoco.
        """
        # Pre-condición: Reducir el saldo de A a 0 (Para forzar la falla)
        self.user_a.profile.saldo_cr = 0
        self.user_a.profile.save()
        
        # Condiciones Iniciales: Saldo A=0, Saldo B=2
        self.assertEqual(self.user_a.profile.saldo_cr, 0)
        self.assertEqual(self.user_b.profile.saldo_cr, 2)
        
        # Ejecutar la lógica atómica (Debe fallar)
        success, message = finalize_atomic_transaction(self.transaction.id)
        
        # 1. Verificar el resultado de la función
        self.assertFalse(success)
        self.assertIn("Saldo CR insuficiente", message) # Mensaje de error esperado

        # 2. Refrescar los perfiles (para ver si hubo ROLLBACK)
        self.user_a.profile.refresh_from_db()
        self.user_b.profile.refresh_from_db()

        # 3. CRÍTICO: Verificar que los saldos NO cambiaron después del ROLLBACK
        self.assertEqual(self.user_a.profile.saldo_cr, 0, "El saldo A debe permanecer en 0 (ROLLBACK).")
        self.assertEqual(self.user_b.profile.saldo_cr, 2, "El saldo B debe permanecer en 2 (ROLLBACK).")
        
        # 4. Verificar que el estado de la Transacción sigue PENDIENTE
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.estado, 'PENDIENTE')