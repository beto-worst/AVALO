from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import TiposDocumento
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.db.models import Q
from .forms import TiposDocumentoForm
from django.http import HttpResponse
from docx import Document
from django.http import HttpResponse, FileResponse
from docxtpl import DocxTemplate
from docx2pdf import convert
from num2words import num2words
from datetime import datetime
import os
import subprocess
from django.conf import settings
import uuid
from django.contrib.auth.models import User
from datetime import datetime
from .models import Archivos
import mimetypes
from Personas.models import Personas
from MisExpedientes.models import Expedientes,CategoriaExpedientes
from django.core.files.base import ContentFile



@login_required
def index2(request):
    return render(request, 'Documentos/home2.html', {})
    

@login_required
def gen_garantia_index(request):
    return render(request, 'Documentos/GeneraGarantia.html', {})
    

@login_required
def index(request):
    return render(request, 'Documentos/tdocumentoslist.html', {})

@login_required
def index_prestacion_serv(request):
    personas = Personas.objects.all().order_by('-id')
    return render(request, 'Documentos/NuevoDocServicios.html', {'personas': personas})
@login_required
def index_misdocumentos(request):
    user_id = request.user.id
    es_administrador = request.user.groups.filter(name='administrador').exists()
    if es_administrador:
        archivos = Archivos.objects.all()
    else:
        archivos = Archivos.objects.filter(usuario_id=user_id).order_by('-id')

    return render(request, 'Documentos/MisDocumentosListado.html' , {'archivos':archivos, 'es_admin': es_administrador})
@login_required
def NuevoArrendamiento(request):
    personas = Personas.objects.all().order_by('-id')
    return render(request, 'Documentos/NuevoDocArrendamiento.html', {'personas':personas})


@login_required
def generaDocServicios(request):
    if request.method == 'POST':
        return redirect("./")
        

def fecha_formateada():
    # Obtén la fecha actual
    fecha_actual = datetime.now()

    # Mapea los nombres de los meses en español
    nombres_meses = [
        'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
        'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
    ]

    # Extrae el día, mes y año
    dia = fecha_actual.day
    mes = fecha_actual.month
    anio = fecha_actual.year

    # Formatea el día con "DE" y el nombre del mes en mayúsculas
    fecha_formateada = f"{dia} DE {nombres_meses[mes - 1]} DEL {anio}"

    # Imprime la fecha formateada
    return (fecha_formateada)
def convertir_docx_a_pdf(docx_filename):
    try:
        # Generar el nombre del archivo PDF
        pdf_filename = os.path.splitext(docx_filename)[0] + '.pdf'
        # Obtener el directorio de salida (el mismo que el del archivo .docx)
        output_dir = 'media/mis_expedientes/'
        # Comando para convertir el archivo .docx a PDF utilizando LibreOffice
        libreoffice_command = [
            'libreoffice',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir', output_dir,
            os.path.join(settings.BASE_DIR, docx_filename)
        ]

        # Imprimir el comando que se ejecutará
        print("Comando de LibreOffice:", ' '.join(libreoffice_command))

        # Ejecutar el comando desde la terminal
        subprocess.run(libreoffice_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ruta completa al archivo PDF generado
        #pdf_filename = os.path.join(output_dir, pdf_filename)

        return pdf_filename
    except Exception as e:
        # Manejo de excepciones
        print(f"Error al convertir el archivo: {e}")
        return None  # Otra acció
@login_required
def generarDocumento(request):
    if request.method == 'POST':
        try:
            # Carga la plantilla desde un archivo DOCX existente
            
            persona_id = request.POST.get('selPersona')
            print('selPersona', persona_id)
            arrendador_nombre = request.POST.get('txtNombreArrendador')
            arrendador_apellido1 = request.POST.get('txtApellido1Arrendador')
            arrendador_apellido2 = request.POST.get('txtApellido2Arrendador')
            arrendatario_nombre = request.POST.get('txtNombreArrendatario')
            arrendatario_apellido1 = request.POST.get('txtApellido1Arrendatario')
            arrendatario_apellido2 = request.POST.get('txtApellido2Arrendatario')
            arrendatario_cuenta = request.POST.get('txtCuentaBanco')
            arrendatario_CLABE = request.POST.get('txtCLABEArrendatario')
            arrendatario_banco = request.POST.get('txtBanco')
            tel_arrendatario = request.POST.get('txtTelefonoArrendador')
            print('EL TELEFONO', tel_arrendatario)
            email_arrendatario = request.POST.get('txtEmailArrendador')
            ##Datos del Domicilio a rentar
            calle_inmueble = request.POST.get('txtCalleInmueble')
            cruzamiento1_inmueble = request.POST.get('txtCruzamiento1Inmueble')
            cruzamiento2_inmueble = request.POST.get('txtCruzamiento2Inmueble')
            colonia_inmueble = request.POST.get('txtcoloniaInmueble')
            cp_inmueble = request.POST.get('txtCPInmueble')
            municipio_inmueble = request.POST.get('txtMunicipioInmueble')
            estado_inmueble = request.POST.get('txtEstadoInmueble')
            cantidad_renta = request.POST.get('txtCantidadRenta')
            cantidad_entero = int(float(cantidad_renta))
            num_palabra = num2words(int(cantidad_entero),lang='es')
            tipo_inmueble = request.POST.get('selectTipoPropiedad')

            dia_corte = request.POST.get('txtDiaCorte')
            fecha_inicio_str = request.POST.get('dateInicio')
            #inicio_contrato = datetime.strptime(fecha_inicio_str, '%d/%b/%Y').date()
            fecha_fin_str = request.POST.get('dateInicio')
            #fin_contrato = datetime.strptime(fecha_fin_str, '%d/%b/%Y').date()
            if 'checkAcepto' in request.POST:
                acepto_terminos = 'PERMITIDO'
            else:
                acepto_terminos = 'PROHIBIDO'

            ##End Datos del Domiclio a rentar
            template = DocxTemplate('PlantiDocs/arrendamiento.docx')
            nombre_archivo = uuid.uuid4()
            docx_filename = 'Documentacion/{}.docx'.format(nombre_archivo)

            # Contexto con variables para llenar la plantilla
            context = {
                'NOMBRE_ARRENDATARIO':'{} {} {}'.format(arrendador_apellido1, arrendador_apellido2, arrendador_nombre),
                'NOMBRE_ARRENDADOR' : '{} {} {}'.format(arrendatario_apellido1, arrendatario_apellido2, arrendatario_nombre),
                'DOMICILIO_INMUEBLE' : '{} POR {}  Y {} DE LA COLONIA {}, CÓDIGO POSTAL: {} EN EL MUNICIPIO DE {}, ESTADO DE {}'.format(calle_inmueble.upper(), cruzamiento1_inmueble.upper(), cruzamiento2_inmueble.upper(), colonia_inmueble.upper(), cp_inmueble,
                                                                                                          municipio_inmueble.upper(), estado_inmueble.upper()),
                'DOMICILIO_INMUEBLE_RENTAR' : '{} POR {}  Y {} DE LA COLONIA {}, CÓDIGO POSTAL: {} EN EL MUNICIPIO DE {}, ESTADO DE {}'.format(calle_inmueble.upper(), cruzamiento1_inmueble.upper(), cruzamiento2_inmueble.upper(), colonia_inmueble.upper(), cp_inmueble,
                                                                                                          municipio_inmueble.upper(), estado_inmueble.upper()),
                'TIPO_USO_INMUEBLE': "{}".format(tipo_inmueble),
                'MONTO_RENTA':'{}'.format(cantidad_renta),
                'MONTO_RENTA_LETRA': num_palabra.upper(),
                'CUENTA_BANCARIA' : arrendatario_cuenta,
                'CLABE':arrendatario_CLABE,
                'NOMBRE_BANCO':arrendatario_banco,
                'MASCOTAS':acepto_terminos,
                'FECHA_CORTE': dia_corte,
                'INICIO_CONTRATO': fecha_inicio_str,
                'FIN_CONTRATO': fecha_fin_str,
                'TEL_ARRENDATARIO': tel_arrendatario,
                'EMAIL_ARRENDATARIO': email_arrendatario,
                'FECHA_FIRMA': fecha_formateada(),
                'contenido': 'Este es un párrafo dinámico en el documento generado.',
            }

            # Rellena la plantilla con el contexto
            template.render(context)

            # Configura la respuesta HTTP
            #response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            #response['Content-Disposition'] = 'attachment; filename="mi_documento.docx"'

            # Guarda el documento en la respuesta
            template.save(docx_filename)

            # Convertir el archivo .docx a PDF
            pdf_filename = convertir_docx_a_pdf(docx_filename)

            fichero = Archivos()
            fichero.tipo_id = 1
            fichero.usuario = request.user
            fichero.uuid_archivo = nombre_archivo
            persona = Personas(id=persona_id)
            fichero.persona = persona
            fichero.save()
            
            #guardar expediente
            try:
                print('guardar expediente (DOCUMENTO)')
                print('ruta archivo ', pdf_filename)
                categoria =  CategoriaExpedientes.objects.get(id=2)
                expediente = Expedientes(expediente_categoria_id=categoria)
                expediente.usuario_id = request.user.id
                expediente.cliente_id = persona_id
                archivo_contenido = open("media/mis_expedientes/{}.pdf".format(nombre_archivo), 'rb').read()
                    # Crear un objeto ContentFile con el contenido del archivo
                archivo_content_file = ContentFile(archivo_contenido)
                expediente.expediente_nombre.save("{}.pdf".format(nombre_archivo), archivo_content_file)
                expediente.save()
            except Exception as e:
                print('Error en guardar expediente', e)
            #guardar expediente

            # Abrir el archivo PDF generado y leer su contenido
            with open( "media/mis_expedientes/{}.pdf".format(nombre_archivo), 'rb') as pdf_file:
            #with open( pdf_filename, 'rb') as pdf_file:
                
                pdf_content = pdf_file.read()

            # Configurar la respuesta HTTP para el archivo PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{"media/mis_expedientes/{}.pdf".format(nombre_archivo)}"'
            #response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_filename)}"'

            # No es necesario eliminar los archivos temporales si están en /tmp, el sistema operativo se encargará de limpiarlos

            return response
        except Exception as e:
            print('Ocurrio un error: ', e)


@login_required
def descargar_documentoPDF(request, name):
    # Abrir el archivo PDF generado y leer su contenido
    pdf_filename = "Documentacion/{}.pdf".format(name)
    with open(pdf_filename, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Configurar la respuesta HTTP para el archivo PDF
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_filename)}"'
    return response


@login_required
def descargar_documentoDOCX(request, name):
    filepath = os.path.abspath(r'Documentacion/{}.docx'.format(name))
    print('SLA FILE: ', filepath)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as worddoc:  # read as binary
            content = worddoc.read()  # Read the file
            response = HttpResponse(
                content,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename={}.docx'.format(name)
            response['Content-Length'] = len(content)  # calculate length of content
            return response
    else:
        return HttpResponse("Failed to Download SLA")



class TiposDocumento_List(LoginRequiredMixin, ListView):
    paginate_by = 10
    model = TiposDocumento
    template_name = 'Documentos/tdocumentoslist.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qsearch = self.request.GET.get('txtSearch')
        queryset = TiposDocumento.objects.all().order_by('id')
        if qsearch:
            queryset = queryset.filter(Q(nombre__icontains=qsearch) | Q(clave__icontains=qsearch) 
                                       | Q(descripcion__icontains=qsearch))
        return queryset
    

class TiposDocumento_Add(LoginRequiredMixin, CreateView):
    model = TiposDocumento
    form_class = TiposDocumentoForm
    template_name = 'Documentos/tdocumentosadd.html'
    success_url = '/Documentos/TiposDocumento'


class TiposDocumento_Edit(LoginRequiredMixin, UpdateView):
    model = TiposDocumento
    form_class = TiposDocumentoForm
    pk_url_kwarg = 'pk'
    template_name = 'Documentos/tdocumentosedit.html'
    success_url = '/Documentos/TiposDocumento'


class TiposDocumento_Delete(LoginRequiredMixin, DeleteView):
    model = TiposDocumento
    template_name = 'Documentos/tdocumentosdelete.html'
    success_url = '/Documentos/TiposDocumento'