from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class NuevoUsuario(forms.Form):
    nombre = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control-sm'}))
    apellido = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control-sm'}))
    apellido2 = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control-sm'}))
    correo = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control-sm'}))
    psw = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control-sm'}))
    pswconfirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control-sm'}))

    def clean_psw(self):
        psw = self.cleaned_data.get('psw')
        # Agrega tus validaciones de contraseña aquí, por ejemplo:
        if len(psw) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return psw

    def clean_pswconfirm(self):
        pswconfirm = self.cleaned_data.get('pswconfirm')
        if len(pswconfirm) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        # Agrega tus validaciones de confirmación de contraseña aquí, si es necesario
        return pswconfirm

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')

        # La vista guarda el correo como nombre de usuario, asi que hay que
        # revisar los dos campos: si solo se valida 'email' y ya existe alguien
        # con ese 'username', el alta revienta con IntegrityError (error 500).
        if User.objects.filter(email__iexact=correo).exists() or \
           User.objects.filter(username__iexact=correo).exists():
            raise forms.ValidationError("El correo electrónico ya está registrado, por favor elige otro.")

        # Devolver el valor validado del correo
        return correo

    def clean(self):
        cleaned_data = super().clean()
        psw = cleaned_data.get('psw')
        pswconfirm = cleaned_data.get('pswconfirm')

        if psw and pswconfirm and psw != pswconfirm:
            raise forms.ValidationError("Las contraseñas no coinciden, intenta de nuevo.")

