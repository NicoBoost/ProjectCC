from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm
from django.contrib import messages
from django.db import models
from marketplace.models import Publication
from core.utils import haversine_distance

# -------------------------------------------------------------------
# 1. Vista de Registro (HU-01)
# -------------------------------------------------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # El signal en profiles/models.py se encarga de crear el Profile
            # con el saldo_cr = 2 automáticamente al guardar el user.
            messages.success(request, f'¡Cuenta creada con éxito! Se te asignaron 2 CR de bienvenida.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})

# -------------------------------------------------------------------
# 2. Vista Principal (Home) - Requiere Login (HU-05)
# -------------------------------------------------------------------
@login_required
def index_view(request):
    user_profile = request.user.profile
    saldo_actual = user_profile.saldo_cr
    
    # 1. Obtener la ubicación del usuario logueado (Origen para el cálculo)
    user_lat = user_profile.coordenada_lat
    user_lon = user_profile.coordenada_lon

    publications = Publication.objects.filter(activo=True).select_related('user__profile', 'skill').exclude(user=request.user)
    
    query = request.GET.get('q')
    if query:
        publications = publications.filter(
            models.Q(titulo__icontains=query) | models.Q(descripcion__icontains=query)
        )
    
    publications_with_distance = []
    
    # 2. Calcular distancia y enriquecer cada publicación
    if user_lat and user_lon:
        for pub in publications:
            target_lat = pub.user.profile.coordenada_lat
            target_lon = pub.user.profile.coordenada_lon

            # Asegurar que la publicación tenga coordenadas válidas
            if target_lat and target_lon:
                distance = haversine_distance(user_lat, user_lon, target_lat, target_lon)
                pub.distance_km = distance
                publications_with_distance.append(pub)
            
        # 3. Ordenar por distancia (Geo-matching)
        publications_with_distance.sort(key=lambda p: p.distance_km)
    else:
        # Si el usuario no tiene ubicación, muestra por fecha (orden por defecto)
        publications_with_distance = list(publications)

    context = {
        'saldo_cr': saldo_actual,
        'publications': publications_with_distance,
        'query': query,
        'is_geo_sorted': user_lat and user_lon
    }
    return render(request, 'index.html', context)