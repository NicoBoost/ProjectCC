from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PublicationForm
from .models import Publication

@login_required
def create_publication(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            # Asignar el usuario actual antes de guardar
            publication = form.save(commit=False)
            publication.user = request.user
            publication.save()
            return redirect('index') # Redirigir al inicio o al detalle
    else:
        form = PublicationForm()
        
    return render(request, 'marketplace/create_publication.html', {'form': form})