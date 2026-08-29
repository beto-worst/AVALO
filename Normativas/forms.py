from django import forms
from .models import Usodesuelo, SustentoLegal


class SustentoLegalForm(forms.ModelForm):
    class Meta:
        model = SustentoLegal
        fields = ['tipo', 'nombre', 'articulo','municipio']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.Select(attrs={'class': 'form-control'})
        }


class UsodeSueloForm(forms.ModelForm):
    class Meta:
        model = Usodesuelo
        fields = ['uso', 'sustento']
        widgets = {
            'uso': forms.TextInput(attrs={'class': 'form-control'}),
            'sustento': forms.Select(attrs={'class': 'form-control'}),
        }