from django import forms
from .models import Municipios, Estados, Paises


class MunicipiosForm(forms.ModelForm):
    estado = forms.ModelChoiceField(queryset=Estados.objects.all())

    class Meta:
        model = Municipios
        fields = ['clave', 'municipio', 'estado']
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }


class EstadosForm(forms.ModelForm):
    pais = forms.ModelChoiceField(queryset=Paises.objects.all())

    class Meta:
        model = Estados
        fields = ['clave', 'estado', 'pais']
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }