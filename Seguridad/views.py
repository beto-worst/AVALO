from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from .forms import RegistroForm, NuevoUsuario
from django.contrib.auth.models import User
from .models import CustomUser
import bcrypt
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return HttpResponseRedirect('/')  # Redirige a una página después del inicio de sesión exitoso.
            else:
                # Mensaje de error si las credenciales son inválidas
                error_message = "Invalid login credentials. Please try again."
                return render(request, 'Seguridad/login2.html', {'form': form, 'error_message': error_message})
        else:
            form = AuthenticationForm()
            return render(request, 'Seguridad/login2.html', {'form': form})


def custom_login(request):
    pass


def custom_logout(request):
    logout(request)
    return redirect('/login')


class RegistroView(FormView):
    template_name = 'Seguridad/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Guarda los datos del usuario en la base de datos
        form.save()

        return super().form_valid(form)


def RegistrarseView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = NuevoUsuario(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido1 = form.cleaned_data['apellido']
            apellido2 = form.cleaned_data['apellido2']
            password = form.cleaned_data['psw']
            email = form.cleaned_data['correo']
            new_user = User(username=email, first_name=nombre, email=email,
                            last_name="{} {}".format(apellido1, apellido2), is_staff=False)
            # set_password() aplica el hasher de Django. Un hash bcrypt crudo no lo
            # reconoce check_password(), y el usuario no volvia a poder entrar.
            new_user.set_password(password)
            new_user.save()
            new_custom_user = CustomUser(usuario_id=new_user.id, nombre=nombre,
                                         apellido1=apellido1, apellido2=apellido2)
            new_custom_user.save()
            #logea al usuario
            user = login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            # Redirigir al usuario a la página principal o a donde desees después del inicio de sesión
            return HttpResponseRedirect('/')
        else:
            # Aquí es donde se renderiza la plantilla con el formulario y los errores de validación
            return render(request, "Seguridad/registrarse2.html", {'form': form})
    else:
        form = NuevoUsuario()
        return render(request, "Seguridad/registrarse2.html", {'form': form})


def getProfile(request):
    if request.user.is_authenticated:
        user_loged = request.user
        usuario = User.objects.get(id=request.user.id)
        #user_custom = CustomUser.objects.get(usuario=user_loged)
        return render(request, 'Seguridad/userprofile.html', {'user': usuario})
    else:
        return HttpResponseRedirect('/login')


def handler404(request, exception, template_name="Error.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña ha sido actualizada exitosamente!')
            return HttpResponseRedirect('/login')  # Cambiar a la URL de perfil adecuada
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'Seguridad/resetpsw.html', {'form': form})
