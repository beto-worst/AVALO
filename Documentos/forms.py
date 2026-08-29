from django import forms
from .models import TiposDocumento, FormatosDocumento


class TiposDocumentoForm(forms.ModelForm):
    class Meta:
        model = TiposDocumento
        fields = ['clave', 'nombre', 'descripcion']
        labels = {
            'clave': 'Clave',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    
class FormatosDocumentoForm(forms.ModelForm):
    class Meta:
        model = FormatosDocumento
        fields = ['tipo', 'clave', 'nombre', 'version', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'ckeditor'})
        }