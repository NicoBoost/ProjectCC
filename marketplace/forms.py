# /marketplace/forms.py
from django import forms
from .models import Publication

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titulo', 'descripcion', 'skill', 'tipo_anuncio']