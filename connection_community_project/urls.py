from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from marketplace import views as marketplace_views
from transactions import views as transaction_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')), # Incluye /login/, /logout/, etc.
    path('register/', core_views.register_view, name='register'),
    path('', core_views.index_view, name='index'),
    path('publicar/', marketplace_views.create_publication, name='create_publication'),
    path('transaccion/iniciar/<int:publication_id>/', transaction_views.start_transaction, name='start_transaction'),
    path('transaccion/finalizar/<int:transaction_id>/', transaction_views.finalize_transaction, name='finalize_transaction'),
    path('transaccion/cancelar/<int:transaction_id>/', transaction_views.cancel_transaction, name='cancel_transaction'),
    path('', core_views.index_view, name='index'),
]
