from django import forms
from .models import Expedientes
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

# https://simpleisbetterthancomplex.com/tutorial/2018/08/13/how-to-use-bootstrap-4-forms-with-django.html

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160

MAX_UPLOAD_SIZE = "2621440"


class ExpeditensForm(forms.ModelForm):

    def clean(self):
        self.check_file()
        return self.cleaned_data

    def check_file(self):
        content = self.cleaned_data['expediente_nombre']
        # content = self.cleaned_data.get('expediente_nombre')
        if not content:
            raise forms.ValidationError(_("No se ha seleccionado ningun archivo"))
        if content.size > int(MAX_UPLOAD_SIZE):
            raise forms.ValidationError(_("Mantenga el tamaño del archivo por debajo de %s. Tamaño de archivo actual %s")%(filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(content.size)))
        return content

    class Meta:
        model = Expedientes
        fields = ['usuario_id', 'cliente_id', 'expediente_categoria_id', 'expediente_nombre']
        widget = {"expediente_nombre": forms.FileField(required=True)}
