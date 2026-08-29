from django import forms
from .models import Personas
from Generales.models import Municipios, Estados, Colonia


class PersonasForms(forms.ModelForm):
    estado = forms.ModelChoiceField(Estados.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    municipio = forms.ModelChoiceField(Municipios.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    colonia = forms.ModelChoiceField(Colonia.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    class Meta:
        model = Personas
        fields = ['rfc', 'curp', 'razonsocial', 'nombre', 'apellido1', 'apellido2', 'estadocivil', 'fnacimiento',
                  'lugarNacimiento', 'telefono_principal', 'telefono_secundario', 'correo_electronico', 'calle',
                  'cruzamiento1', 'cruzamiento2', 'estado', 'municipio', 'colonia', 'tipo', 'direccionine']

        widgets = {
            'rfc': forms.TextInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'razonsocial': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido1': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido2': forms.TextInput(attrs={'class': 'form-control'}),
            'estadocivil': forms.Select(attrs={'class': 'form-select'}),
            'fnacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'lugarNacimiento': forms.Select(attrs={'class': 'form-select'}),
            'telefono_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_secundario': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'cruzamiento1': forms.TextInput(attrs={'class': 'form-control'}),
            'cruzamiento2': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.TextInput(attrs={'class': 'form-select'}),
            'colonia': forms.TextInput(attrs={'class': 'form-select'}),
            'tipo': forms.TextInput(attrs={'class': 'form-select'}),
            'direccionine': forms.TextInput(attrs={'class': 'form-control'}),
        }
