from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import render
import tempfile
from django.http import HttpResponse
from django.core.files import File
from django.views.decorators.http import require_http_methods, require_POST
import base64
import json
import requests
import pandas as pd
import re
import os
from LegalBit import report
import environ
from Investigaciones.models import Investigacion, InvestigacionPremium
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseServerError
from unidecode import unidecode
import requests
import json
from Personas.models import Personas
from django.http import HttpResponseRedirect
from Generales.models import EstadosCiviles, Paises, LugarNacimientoCURP
from datetime import datetime
from datetime import  date
import locale
from django.template.loader import render_to_string
import demjson3
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render
from Seguridad.models import ConfiguracionUsuariosLB
from LegalBit.report import ReportService
from django.contrib.auth.models import User
import numpy as np
from MisExpedientes.models import Expedientes,CategoriaExpedientes
import uuid
from Webhook.models import reponses
from django.conf import settings
import uuid
from django.http import FileResponse
from django.shortcuts import render
# Obtén la ruta base del proyecto
base_dir = settings.BASE_DIR
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist
from demjson3 import JSONDecodeError
import traceback
from io import BytesIO
from playwright.sync_api import sync_playwright
import tempfile
import uuid as uuid_lib
from django.core.files.base import ContentFile


@login_required
def index_investigacion_premium(request):
    user_id = request.user.id
    personas = Personas.objects.filter(usuario_id=user_id).order_by('-id')
    return render(request, 'InvPremium/inicio.html', {'personas':personas})

@login_required
def get_imss_by_personid(request, id):
    try:
        obj = Personas.objects.get(id=id)
        imss = get_imss_api(obj.curp)
        imss_data =  demjson3.decode(imss)
        imss_uuid =  imss_data["body"]["data"]["transactionId"]
        obj.uuid_imss = imss_uuid
        obj.save()
    except Exception as e:
        print(e)

def get_imss_api(curp):
    env = environ.Env()
    #
    url = "https://api.mox.cash/v1/income-verification"

    payload = json.dumps({
    "curp": "{}".format(curp),
    "hook": "http://sistema.legalbit.mx/Webhook/20e355df03730ba3d1a98c7f95673a3c"
    })
    headers = {
    'Content-Type': 'application/json',
    'x-api-key': '{}'.format(env('MOX_KEY'))
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text

def get_issste_api(curp):
    env = environ.Env()
    url = "https://api.mox.cash/v1/income-verification/issste"

    payload = json.dumps({
    "curp": "{}".format(curp),
    "hook": "http://sistema.legalbit.mx/Webhook/20e355df03730ba3d1a98c7f95673a3c"
    })
    headers = {
    'Content-Type': 'application/json',
    'x-api-key': '{}'.format(env('MOX_KEY'))
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text



@login_required
def escaneo_index(request):
    if request.method == 'GET':
        return render(request, 'Investigaciones/escanear_ine.html', {})
    if request.method == 'POST':
        archivo = request.FILES.get('file1')
        archivo2 = request.FILES.get('file2')
        tipo_ine = request.POST.get('selINE')
        archivo_uuid = str(uuid.uuid4())  # Genera un UUID único
        archivo_uuid2 = str(uuid.uuid4())  # Genera un UUID único

        # Agrega una extensión de archivo, por ejemplo '.png'
        nombre_archivo = archivo_uuid+'.jpg'
        nombre_archivo2 = archivo_uuid2+'.jpg'
        # os.chdir eliminado: cambiaba el directorio de trabajo de TODO el proceso.
        rutaArchivo = os.path.join(base_dir, 'uploads', nombre_archivo)
        rutaArchivo2 = os.path.join(base_dir, 'uploads', nombre_archivo2)
        print('ruta a archivo ', rutaArchivo)
        with open(rutaArchivo, 'wb') as f:
            for chunk in archivo.chunks():
                f.write(chunk)
        rutaArchivoCompleta = os.path.abspath(rutaArchivo)
        # Ahora utiliza el nombre del archivo con UUID para procesarlo
        print('CORTAR IMAGEN FRONTA')
        try:
            cortar_y_guardar_rectangulo(rutaArchivoCompleta, os.path.join(base_dir, 'uploads', 'CUT_'+nombre_archivo))
        except Exception as ex:
            print('ERROR ', ex)
        print('ruta al archivo ', rutaArchivoCompleta)
        #back
        with open(rutaArchivo2, 'wb') as f:
            for chunk in archivo2.chunks():
                f.write(chunk)
        rutaArchivoCompleta2 = os.path.abspath(rutaArchivo2)
        print('CORTAR IMAGEN 2')
        cortar_y_guardar_rectangulo2(rutaArchivoCompleta2, os.path.join(base_dir, 'uploads', 'BACK_'+nombre_archivo2))
        valida_ine = '.'
        cic = ''
        ocr_idc = ''
        try:
            #curp, clave_elector = extraer_curp_y_clave_elector(os.path.join('uploads', 'CUT_'+nombre_archivo))
            try:
                curp, clave_elector = extraer_curp_y_clave_elector(os.path.join(base_dir, 'uploads','CUT_'+nombre_archivo))
            except Exception as e:
                print('ERROR DELANTERO', e)
            try:
                cic, ocr_idc = obtener_cic_y_ocr(os.path.join(base_dir, 'uploads', 'BACK_'+nombre_archivo2))
                print('CIC ,OCR', cic, ocr_idc)
                valida_ine = validaListaNominal2(tipo_ine, cic, ocr_idc)
                print('validacion ine ', valida_ine)
            except Exception as e:
                print('Ocurrio un error al leer la parte trasera de la INE ', e)
            curp2 =  str(convertir_ultimos_digitos(curp)).strip()
           
            print('ultimos digitos', curp[-3:] ,'lacurtp es :',len(curp2), str(curp2).strip(),'archivo ',os.path.join('uploads', 'CUT_'+nombre_archivo))
            if curp is not None or clave_elector is not None or cic is not None or ocr_idc is not None:
                 try:
                     print('JSON CURP', obtenerDatosCURP2(curp2))
                     data = demjson3.decode(obtenerDatosCURP2(curp2))
                     print('obtener datos API ',data )
                     print('campo error', data['status'])
                     if  data['status'] != 'error':
                        curp_val = data["data"]["curpdata"][0]["curp"]
                        nombre = data["data"]["curpdata"][0]["nombres"]
                        apellido_paterno = data["data"]["curpdata"][0]["primerApellido"]
                        apellido_materno = data["data"]["curpdata"][0]["segundoApellido"]
                        fecha_nacimiento  = data["data"]["curpdata"][0]["fechaNacimiento"]
                        partes = fecha_nacimiento.split('/')
                        # Convertir las partes en enteros
                        dia = int(partes[0])
                        mes = int(partes[1])
                        anio = int(partes[2])
                        dia_formateado = str(dia).zfill(2)
                        mes_formateado = str(mes).zfill(2)
                        print('nombre es', nombre, apellido_paterno, apellido_materno, fecha_nacimiento, curp_val)
                        print('FECHA NACIEMIENTO dia mes anio ' , dia, mes , anio)
                        calcRFCJSON = calculadoraRFC3(nombre,apellido_paterno,apellido_materno, dia_formateado, mes_formateado,anio)
                        data_rfc = demjson3.decode(calcRFCJSON)
                        # Accede al valor del RFC
                        rfc = data_rfc["data"]["rfc"]
                        #imss = get_imss_api(curp_val)
                        #issste = get_issste_api(curp_val)
                        #imss_data =  demjson3.decode(imss)
                        #issste_data = demjson3.decode(issste)
                        #print('IMSS JSON', imss_data)
                        #print('ISSSTE JSON', issste_data)
                        #imss_uuid =  imss_data["body"]["data"]["transactionId"]
                        #issste_uuid =  issste_data["metaData"]["transactionId"]
                        print('RFC CALCULADO ', calcRFCJSON)
                        persona = Personas()
                        persona.nombre = nombre
                        persona.rfc = rfc
                        persona.direccionine = '.'
                        persona.inejson = '.'
                        persona.inejson2 = '.'
                        persona.manual = True
                        persona.cic_ine = cic
                        persona.identificador_ine = ocr_idc
                        persona.clave_elector = clave_elector
                        persona.razonsocial = '{} {} {}'.format(nombre, apellido_paterno, apellido_paterno)
                        persona.curp = curp_val
                        persona.apellido1 = apellido_paterno
                        persona.apellido2 = apellido_materno
                        persona.validaine = valida_ine
                        persona.inerevers = os.path.join('uploads', 'BACK_'+nombre_archivo2)
                        persona.inefront = os.path.join('uploads', 'BACK_'+nombre_archivo)
                        persona.direccionine = '.'
                        persona.estadocivil_id = 1
                        persona.estado_id=1
                        persona.municipio_id = 1
                        persona.colonia_id = 1
                        persona.lugarNacimiento_id = 1
                        persona.correo_electronico = 'persona@legalbit.mx'
                        persona.usuario = request.user
                        persona.uuid_imss = 'NA'
                        persona.uuid_issste = 'NA'
                        persona.tipo = 'PF'
                        try:
                            persona.save()
                        except Exception as e:
                             return render(request, 'Investigaciones/escanear_ine.html', {'hubo_error':e})
                            
                     else:
                        return render(request, 'Investigaciones/escanear_ine.html', {'hubo_error':e})
                     #return HttpResponseRedirect('/')
                 except Exception as e:
                     print('error al validar CURP, ',e)
                     
                 return HttpResponseRedirect('/')
                 #return render(request, 'Investigaciones/escanear_ine.html', {'curp':curp2, 'clave_elector':clave_elector})
            else:
                return render(request, 'Investigaciones/escanear_ine.html', {'hubo_error':'OCURRIO UN ERROR AL OBTENER DATOS DE LA INE, INTENTE DE NUEVO 1'})
        except Exception as e:
             return render(request, 'Investigaciones/escanear_ine.html', {'hubo_error':'OCURRIO UN ERROR AL OBTENER DATOS DE LA INE, INTENTE DE NUEVO 2'})
            
            

def reemplazar_letra_o(cadena):
    # Utilizar una expresión regular para buscar 'O' seguida de un número
    patron = r'O(\d)'
    def reemplazo(match):
        return '0' + match.group(1)

    # Aplicar la función de reemplazo a la cadena
    cadena_corregida = re.sub(patron, reemplazo, cadena)

    return cadena_corregida

cadena_original = "Esto es un ejemplo con O4 y O7."
cadena_corregida = reemplazar_letra_o(cadena_original)
    
def convertir_ultimos_digitos(curp):
    # Verificar si la CURP tiene al menos 18 caracteres
    if len(curp) >= 18:
        # Obtener los dos últimos caracteres
        ultimos_dos = curp[-3:]
        ultimos_dos = ultimos_dos.replace('O','0')
        curp = curp[:-3] + ultimos_dos

    return curp


def valida_IMSS(curp):
    env = environ.Env()
    url = "https://api.mox.cash/v1/income-verification"

    payload = json.dumps({
    "curp": "{}".format(curp),
    "hook": "http://sistema.legalbit.mx/Webhook/20e355df03730ba3d1a98c7f95673a3c"
    })
    headers = {
    'Content-Type': 'application/json',
    'x-api-key': '{}'.format(env('MOX_KEY'))
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

@login_required
def nuevo_home(request):
    return render(request,'Investigaciones/nuevoHome.html',{})

@login_required
def index(request):
    if request.method == 'POST' and not 'validaRENAPO' in request.POST:
        error = ""
        archivo = request.FILES.get('userfile')
        archivo2 = request.FILES.get('userfile2')
        # El nombre lo elige el servidor, nunca el cliente: archivo.name permite rutas
        # tipo '../..' y escribiria fuera de uploads/.
        rutaArchivo = os.path.join(base_dir, 'uploads', '{}.jpg'.format(uuid.uuid4()))
        rutaArchivo2 = os.path.join(base_dir, 'uploads', '{}.jpg'.format(uuid.uuid4()))
        with open(rutaArchivo, 'wb') as f:
            for chunk in archivo.chunks():
                f.write(chunk)
        with open(rutaArchivo2, 'wb') as f:
            for chunk in archivo2.chunks():
                f.write(chunk)
        rutaArchivoCompleta = os.path.abspath(rutaArchivo)
        rutaArchivoCompleta2 = os.path.abspath(rutaArchivo2)
        foto = image_to_base64(rutaArchivoCompleta)
        foto2= image_to_base64(rutaArchivoCompleta2)
        #respuesta = validarINE(rutaArchivoCompleta)
        respuesta = extraeINEFrontal(rutaArchivoCompleta)
        respuesta2 = extraeINETrasero(rutaArchivoCompleta2)
        data2 = json.loads(respuesta2)
        #print(data2)
        data = json.loads(respuesta)
        request.session['inejson'] = ""
        request.session['inejson'] = data
        request.session['inejson2'] = ""
        request.session['inejson2'] = data2
        print(data2)
        if data2['status'] == 'error':
            error = 'Ha ocurrido un error en el servicio de INE, por lo que deberá capturar el OCR de manera manual'
            
        calcRFCJSON = calculadoraRFC(data['data']['ocr']['nombre'], data['data']['ocr']['apellido_paterno'],
                                     data['data']['ocr']['apellido_materno'], data['data']['ocr']['fecha_nacimiento'])
        #print("RFC service ", calcRFCJSON)
        request.session['RFCJSON'] = ''
        request.session['RFCJSON'] = calcRFCJSON

        return render(request, 'Investigaciones/index.html', {'apellido1': data['data']['ocr']['apellido_paterno'],
                                                              'nombres': data['data']['ocr']['nombre'],
                                                              'apellido2': data['data']['ocr']['apellido_materno'],
                                                              'curp': data['data']['ocr']['curp'],
                                                              'direccion': data['data']['ocr']['calle_numero'],
                                                              'sexo': '',
                                                              'fnac': data['data']['ocr']['fecha_nacimiento'],
                                                              'foto': foto, 'lleno': True, 'error':error , 'foto2':foto2})
    if request.method == 'POST' and 'validaRENAPO' in request.POST:
        env = environ.Env()
        curp = request.POST.get('curp')
        direccion = request.POST.get('direccion')
        sexo = request.POST.get('selSexo')

        rfcjson = request.session['RFCJSON']
        datarfc = json.loads(rfcjson)
        #url = "https://sandbox.moffin.mx/api/v1/query/renapo_curp"
        url = "https://app.moffin.mx/api/v1/query/renapo_curp"
        payload = json.dumps({
            "curp": "{}".format(curp),
            "accountType": "PF"
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': env('MOFFIN_APIKEY')
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        #print(response.text)
        nombreRENAPO = ""
        if response.status_code == 201:
            # Parsear el JSON de la respuesta en un diccionario
            response_dict = response.json()
            print(response_dict)
            estadosciv = EstadosCiviles.objects.all()
            # Acceder a los valores del diccionario
            curpRENAPO = response_dict['response']['curp']
            nombreRENAPO = response_dict['response']['nombre']
            apellido_paterno = response_dict['response']['apellidoPaterno']
            apellido_materno = response_dict['response']['apellidoMaterno']
            fechanacRENAPO = response_dict['response']['fechaNacimiento']
            sexoRENAPO = response_dict['response']['sexo']
            paisRENAPO = response_dict['response']['paisNacimiento']
            entidadRENAPO = response_dict['response']['datosDocProbatorio']['entidadRegistro']
            municipioRENAPO = response_dict['response']['datosDocProbatorio']['municipioRegistro']

        return render(request, 'Investigaciones/valida_renapo.html', {'apellido1': apellido_paterno,
                                                                      'nombres': nombreRENAPO,
                                                                      'apellido2': apellido_materno,
                                                                      'curp': curp,
                                                                      'direccion': direccion,
                                                                      'sexo': sexo,
                                                                      'fnac': '',
                                                                      'rfc': datarfc['data']['rfc'],
                                                                      'nombreRENAPO': nombreRENAPO,
                                                                      'apellido1RENAPO': apellido_paterno,
                                                                      'apellido2RENAPO':apellido_materno,
                                                                      'fechaNacRENAPO' : fechanacRENAPO,
                                                                      'curpRENAPO': curpRENAPO,
                                                                      'sexoRENAPO': sexoRENAPO,
                                                                      'paisRENAPO': paisRENAPO,
                                                                      'entidadRENAPO':entidadRENAPO,
                                                                      'municipioRENAPO':municipioRENAPO,
                                                                      'estadosciviles' : estadosciv,
                                                                      })

    else:
        return render(request, 'Investigaciones/index.html')
    

@login_required
def InvestigadoManual(request):
    if request.method == 'GET':
        return render (request, 'Investigaciones/investigacion_manual.html',{})
    
@login_required
def iniciar_antecedentesnac(request):
    pass

@login_required
def iniciarInvestigacion(request):
    if request.method == 'GET':
        user_id = request.user.id  # Obtener el ID del usuario logueado
        # Filtrar investigaciones por el ID del usuario logueado
        #objects_list = Investigacion.objects.filter(usuario_id=user_id).order_by('-id
        personas = Personas.objects.filter(usuario_id=user_id).order_by('-id')
        return render(request, 'Investigaciones/iniciar_investigacion.html', {'personas': personas})
    if request.method == 'POST':
        persona_id = request.POST.get('personaID')
        print('persona valor investigacion:', persona_id)
        user_id = request.user.id  # Obtener el ID del usuario logueado
        # Filtrar investigaciones por el ID del usuario loguead
        get_user_config = ConfiguracionUsuariosLB.objects.get(usuario_id=user_id)
        num_investigaciones = Investigacion.objects.filter(usuario_id=user_id).count()
        if persona_id is not None and persona_id != "0" and persona_id != "": 
            if num_investigaciones <= get_user_config.max_investigaciones:
                last_id = Investigacion.objects.last().folio + 1
                persona = Personas.objects.get(id=persona_id)
                investigacion = Investigacion()
                investigacion.usuario = request.user
                investigacion.investigado = persona
                investigacion.folio = last_id
                investigacion.nombre_archivo='ND'
                investigacion.save()
                errores = ""
                investigacion.usuario = request.user
                investigacion.nombre_archivo = "ND"
                investigacion.investigado = persona
                investigacion.save()
                env = environ.Env()
                print('INvestigacion POST')
                
                print('persona', persona)
                lista_negraintl = 'ND'
                try:
                    lista_negraintl = getListaNegraIntl("{} {} {}".format(persona.nombre, persona.apellido1, persona.apellido2))
                except Exception as e:
                    print(e)
                antecedentesjson = 'ND'
                try:
                    antecedentesjson = obtenerAntecedentes(persona.nombre, persona.apellido1, persona.apellido2)
                    antecedentesjson = demjson3.decode(antecedentesjson)
                except Exception as e:
                    print(e)
                historialAcademico = 'ND'
                try:
                    historialAcademico = obtenerHistorialAcademico(persona.nombre, persona.apellido1, persona.apellido2)
                except Exception as e:
                    print(e)
                print(persona.rfc)
                blackListSAT = 'ND'
                try:
                    blackListSAT = get_blackListSAT(persona.rfc)
                    blackSATJSON = demjson3.decode(blackListSAT)
                except Exception as e:
                    print(e)
                #if resant['code'] == 400 or resant['code'] == 401 or resant['code'] == 403:
                #    errores = errores + "<br> Error al conectar a API Antecedentes {}".format(resant['message'])
                burojson = 'ND'
                score = '0'
                try:
                    burojson = get_reporteBuro(persona_id)
                    resburo = demjson3.decode(burojson)
                    if 'statusCode' in resburo and resburo['statusCode'] is not None:
                        if resburo['statusCode'] == 400 or resburo['statusCode'] == 401 or resburo['statusCode'] == 403:
                            errores = errores + "<br> Error al conectar a la API Buró {}".format(resburo['message'])
                        datascore = json.loads(investigacion.burojson)
                        score = datascore["response"]['json']['score']['value']
                except Exception as e:
                    print(e)

                if errores == "":
                    investigacion.nombre_archivo='ND'
                    investigacion.antecedentesjson = antecedentesjson
                    investigacion.satblacklistjson = blackSATJSON
                    investigacion.burojson = burojson
                    investigacion.listanegraintl = lista_negraintl
                    
                    investigacion.estudiosprofesionalesjson = historialAcademico
                    investigacion.folio = last_id
                    
                    if int(score) > 600:
                        investigacion.aprobado = True
                    else:
                        investigacion.aprobado = False
                    investigacion.nombre_archivo="ND"
                    investigacion.save()
                    try:
                        print('guardando en PDF investigación')
                        verPDF7(request,id=investigacion.id)
                        #investigacion.nombre_archivo = archivo
                        #investigacion.save()
                    except Exception as e:
                        print(e)
                    return HttpResponseRedirect('/Investigaciones/Lista')
                else:
                    return render(request, 'Errores/error.html', {'mensaje': errores ,'url_ant': '/Investigaciones/Lista'})
            else:
                errores ='Excedido el numero de investigaciones permitidas al usuario!'
                return render(request, 'Errores/error.html', {'mensaje': errores, 'url_ant': '/Investigaciones/Lista'})
        else:
            errores ='Debe seleccionar una persona'
            return render(request, 'Errores/error.html', {'mensaje': errores, 'url_ant': '/Investigaciones/IniciarInvestigacion'})
        


@login_required
def calcularCURP(request,entidad,dia,mes,nombre,apellido1,apellido2,anio,sexo):
    import requests
    env = environ.Env()
    url = "https://nufi.azure-api.net/curp/v1/consulta"

    payload = {
        "tipo_busqueda": "datos",
        "clave_entidad": "{}".format(entidad),
        "dia_nacimiento": "{}".format(dia),
        "mes_nacimiento": "{}".format(mes),
        "nombres": "{}".format(nombre),
        "primer_apellido": "{}".format(apellido1),
        "segundo_apellido": "{}".format(apellido2),
        "anio_nacimiento": "{}".format(anio),
        "sexo": "{}".format(sexo)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key":  env('NUFI_API_KEY')
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    return JsonResponse(data, safe=False)



@csrf_exempt
@login_required
def obtenerDatosCURP(request, curp):
     user_id = request.user.id
     get_user_config = ConfiguracionUsuariosLB.objects.get(usuario_id=user_id)
     num_investigaciones = Investigacion.objects.filter(usuario_id=user_id).count()
     if num_investigaciones <= get_user_config.max_investigaciones: 
        import requests
        env = environ.Env()

        url = "https://nufi.azure-api.net/curp/v1/consulta"

        payload = {
            "tipo_busqueda": "curp",
            "curp": "{}".format(curp)
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": env('NUFI_API_KEY')
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        return JsonResponse(data, safe=False)
     else:
        return JsonResponse({}, safe=False)


def obtenerDatosCURP2(curp):
    import requests
    env = environ.Env()

    url = "https://nufi.azure-api.net/curp/v1/consulta"

    payload = {
        "tipo_busqueda": "curp",
        "curp": '{}'.format(curp)
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": env('NUFI_API_KEY')
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print('data curp', response.text)

    return response.text



def obtenerAntecedentes(nombre, apellido1, apellido2):
    env = environ.Env()
    url = "https://nufi.azure-api.net/antecedentes_judiciales/v2/persona_fisica_nacional"

    payload = {
        "nombre": "{}".format(nombre),
        "paterno": "{}".format(apellido1),
        "materno": "{}".format(apellido2),
        "detalle": True,
        "estado": "nacional"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "NUFI-API-KEY": "{}".format(env('NUFI_API_KEY'))
    }
    response = requests.post(url, json=payload, headers=headers)
    # print(response.json())
    return response.text


def obtenerHistorialAcademico(nombre, apellido1, apellido2):
    env = environ.Env()
    url = "https://nufi.azure-api.net/CedulaProfesional/consultar"

    payload = {
        "nombre": "{}".format(nombre),
        "apellido_paterno": "{}".format(apellido1),
        "apellido_materno": "{}".format(apellido2),
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.text



@csrf_exempt
@login_required
def addPersonaAPI(request):
    print('llamada a API agregar')
    if request.method == 'POST':
        datos_json = json.loads(request.body.decode('utf-8'))
        print(datos_json)
        nombre = datos_json.get('nombre', None)
        apellido1 = datos_json.get('apellido1', None)
        apellido2 = datos_json.get('apellido2', None)
        curp = datos_json.get('curp', None)
        rfc = datos_json.get('rfc', None)
        fechanac = datos_json.get('fechanac', None)
        lugarnac = datos_json.get('lugarnac', None)
        estadoobj = LugarNacimientoCURP.objects.filter(clave__iexact=lugarnac).first()
        razonsocial = "{} {} {}".format(nombre, apellido1, apellido2)
        try:
            obj = Personas()
            obj.nombre = nombre
            obj.apellido1 = apellido1
            obj.apellido2 = apellido2
            obj.razonsocial = razonsocial
            obj.fnacimiento = fechanac
            obj.rfc = rfc
            obj.uuid_issste = 'NA'
            obj.uuid_imss ='NA'
            obj.nombre = nombre
            obj.apellido1 = apellido1
            obj.apellido2 = apellido2
            obj.curp = curp
            obj.lugarNacimiento_id = estadoobj.id
            obj.correo_electronico = 'persona@legalbit.mx'
            obj.estadocivil_id = 1
            obj.estado_id=1
            obj.municipio_id = 1
            obj.colonia_id = 1
            obj.tipo = 'PF'
            obj.validaine = 'ND'
            obj.manual = True
            obj.clave_elector = 'ND'
            obj.cic_ine = 'ND'
            obj.usuario = request.user
            obj.identificador_ine = 'ND'
            #if archivo1:
            #    obj.inefront.save(archivo1.name, archivo1)
            #if archivo2:
            #    obj.inerevers.save(archivo2.name, archivo2)
            obj.save()
             # Puedes devolver una respuesta JSON si es necesario
            respuesta = {'id': obj.id}
            return JsonResponse(respuesta)
            print("guardado ")
            
        except Exception as e:
            print('Error al agregar', e)
        
@login_required
def addPersonaManual(request):
    if request.method == 'POST':
        user_id = request.user.id
        get_user_config = ConfiguracionUsuariosLB.objects.get(usuario_id=user_id)
        num_investigaciones = Investigacion.objects.filter(usuario_id=user_id).count()
        if num_investigaciones <= get_user_config.max_investigaciones:
            chkValidadINE = request.POST.getlist('chkValINE')
            rfc = request.POST.get('txtRFC')
            curp = request.POST.get('txtCURP')
            nombre = request.POST.get('txtNombre')
            apellido1 = request.POST.get('txtApellido1')
            apellido2 = request.POST.get('txtApellido2')
            fechaNac = request.POST.get('txtFNac')
            print(fechaNac)
            fecha_obj = datetime.strptime(fechaNac, '%Y-%m-%d').date()
            fecha_nueva_str = fecha_obj.strftime('%Y-%m-%d')
            selLugarNacimiento = request.POST.get('selLugarNacimiento')
            estadoobj = LugarNacimientoCURP.objects.filter(clave__iexact=selLugarNacimiento).first()
            razonsocial = "{} {} {}".format(nombre, apellido1, apellido2)
            if 'SI' in chkValidadINE:
                valINE = request.POST.get('valINE')
                clave_elector = request.POST.get('txtClaveElector')
                cic = request.POST.get('txtCIC')
                identificador = request.POST.get('txtIdentificador')
            else:
                valINE = 'ND'
                clave_elector = 'N/A'
                cic = 'N/A'
                identificador = 'N/A'
        
            #archivo1 = request.FILES.get('userfile')
            #archivo2 = request.FILES.get('userfile2')
            #imss = get_imss_api(curp)
            #issste = get_issste_api(curp)
            #imss_data =  demjson3.decode(imss)
            #issste_data = demjson3.decode(issste)
            #imss_uuid =  imss_data["body"]["data"]["transactionId"]
            #issste_uuid =  issste_data["metaData"]["transactionId"]
            obj = Personas()
            obj.razonsocial = razonsocial
            obj.fnacimiento = fecha_nueva_str
            obj.rfc = rfc
            obj.uuid_issste = 'NA'
            obj.uuid_imss ='NA'
            obj.nombre = nombre
            obj.apellido1 = apellido1
            obj.apellido2 = apellido2
            obj.curp = curp
            obj.lugarNacimiento_id = estadoobj.id
            obj.correo_electronico = 'persona@legalbit.mx'
            obj.estadocivil_id = 1
            obj.estado_id=1
            obj.municipio_id = 1
            obj.colonia_id = 1
            obj.tipo = 'PF'
            obj.validaine = valINE
            obj.manual = True
            obj.clave_elector = clave_elector
            obj.cic_ine = cic
            obj.usuario = request.user
            obj.identificador_ine = identificador
            #if archivo1:
            #    obj.inefront.save(archivo1.name, archivo1)
            #if archivo2:
            #    obj.inerevers.save(archivo2.name, archivo2)
            obj.save()
            print('Guardado ', obj.id)
            return HttpResponseRedirect('/')
        else:
            render(request, 'Error.html', {'mensaje':'No tienes suficientes creditos, contacta a soporte.'})  




@login_required
def agregarPersona(request):
    if request.method == "POST" and 'addInvPersona' in request.POST:
        rfc = request.POST.get('rfc')
        nombre = request.POST.get('nombreRENAPO')
        apellido1 = request.POST.get('apellido1RENAPO')
        apellido2 = request.POST.get('apellido2RENAPO')
        curp = request.POST.get('curpRENAPO')
        pais = request.POST.get('paisRENAPO')
        correo = request.POST.get('correo')
        estado = request.POST.get('entidadRENAPO')
        fechanac = request.POST.get('fechaNacRENAPO')
        fecha_obj = datetime.strptime(fechanac, '%d/%m/%Y').date()
        fecha_nueva_str = fecha_obj.strftime('%Y-%m-%d')
        estadoobj = LugarNacimientoCURP.objects.filter(lugarnacimiento__iexact=estado).first()
        print(estadoobj.lugarnacimiento)
        paisobj = Paises.objects.filter(pais__iexact=pais).first()
        direccionINE = request.POST.get('direccion')
        estadoc = request.POST.get('estadoCivil')
        razonsocial = "{} {} {}".format(nombre, apellido1, apellido2)
        obj = Personas()
        obj.usuario_id = request.user.id
        obj.fnacimiento = fecha_nueva_str
        obj.estadocivil_id = 1
        obj.lugarNacimiento_id = estadoobj.id
        obj.correo_electronico = correo
        obj.estado_id=1
        obj.municipio_id = 1
        obj.colonia_id = 1
        obj.tipo = 'PF'
        obj.curp = curp
        obj.rfc = str(rfc).upper()
        obj.nombre = nombre
        obj.apellido1 = apellido1
        obj.apellido2 = apellido2
        obj.razonsocial = razonsocial
        obj.direccionine = direccionINE
        obj.inejson = request.session['inejson']
        obj.inejson2 = request.session['inejson2']
        print("id usuario " ,request.user.id)
        obj.save()
        print('Guardado ', obj.id)
        return HttpResponseRedirect('/')

@login_required
def validaRenapo(request):
    if request.method == 'POST':
        curp = request.POST.get('curp')
        print(curp)


def image_to_base64(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        #if filename.endswith('.png'):
        #    prefix = 'data:image/png;base64,'
        #elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        #    prefix = 'data:image/jpeg;base64,'
        #elif filename.endswith('.gif'):
        #    prefix = 'data:image/gif;base64,'
        #else:
        #    raise ValueError('Unsupported file format')
        #return prefix + base64.b64encode(data).decode('utf-8')
        return base64.b64encode(data).decode('utf-8')


def extraeINEFrontal(archivo):
    env = environ.Env()
    url = "https://nufi.azure-api.net/ocr/v1/frente"

    payload = {
        "base64_credencial_frente" : image_to_base64(archivo),
        "regresar_recortes": True
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text


def extraeINETrasero(archivo):
    env = environ.Env()
    url = "https://nufi.azure-api.net/ocr/v1/reverso"

    payload = {
        "base64_credencial_reverso": image_to_base64(archivo),
        "regresar_recortes": True
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text


def getuuidnss(curp):
    env = environ.Env()
    import requests

    url = "https://nufi.azure-api.net/numero_seguridad_social/v2/consultar"

    querystring = {"curp": "{}".format(curp), "webhook": "https://webhook.site/"}

    headers = {
        "Accept": "application/json",
        "NUFI-API-KEY": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.text

def getListaNegraIntl(nombrecompleto):
    env = environ.Env()
    url = "https://nufi.azure-api.net/perfilamiento/v1/aml"

    payload = {
        "nombre_completo": "{}".format(nombrecompleto),
        "primer_nombre": "",
        "segundo_nombre": "",
        "apellidos": "",
        "fecha_nacimiento": "",
        "lugar_nacimiento": ""
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "NUFI-API-KEY": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)

    return  response.text

@login_required
def validaListaNominal(request, tipo, cic, identificador):
    import requests
    env = environ.Env()

    url = "https://nufi.azure-api.net/v1/lista_nominal/validar"

    if tipo == 'D':
        payload={
        "tipo_identificacion": "{}".format(tipo),
        "cic":'{}'.format(cic),
        "ocr": '{}'.format(identificador),
        }
    if tipo == 'E' or tipo == 'F' or tipo == 'G' or tipo == 'H':
        payload={
        "tipo_identificacion":  "{}".format(tipo),
        "cic": '{}'.format(cic),
        "identificador_del_ciudadano": '{}'.format(identificador),
        }
    #payload = {
    #    "tipo_identificacion": "{}".format(tipo),
    #    "cic": '{}'.format(cic),
    #    "identificador_del_ciudadano": '{}'.format(identificador),
    #    "ocr": 1023123491540,
    #    "clave_de_elector": "HGLPLS92090914H200",
    #    "numero_de_emision": "00"
    #}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return JsonResponse(data, safe=False)

def validaListaNominal2(tipo, cic, identificador):
    import requests
    env = environ.Env()

    url = "https://nufi.azure-api.net/v1/lista_nominal/validar"

    if tipo == 'D':
        payload={
        "tipo_identificacion": "{}".format(tipo),
        "cic":'{}'.format(cic),
        "ocr": '{}'.format(identificador),
        }
    if tipo == 'E' or tipo == 'F' or tipo == 'G' or tipo == 'H':
        payload={
        "tipo_identificacion":  "{}".format(tipo),
        "cic": '{}'.format(cic),
        "identificador_del_ciudadano": '{}'.format(identificador),
        }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return response.text


@login_required
def calculadoraRFC2(request, nombres, apellido1, apellido2, dia,mes,anio):
    env = environ.Env()
    url = "https://nufi.azure-api.net/api/v1/calcular_rfc"
    payload = {
        "nombres": "{}".format(nombres),
        "apellido_paterno": "{}".format(apellido1),
        "apellido_materno": "{}".format(apellido2),
        "fecha_nacimiento": "{}/{}/{}".format(dia,mes,anio)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return JsonResponse(data, safe=False)

def calculadoraRFC3(nombres, apellido1, apellido2, dia,mes, anio):
    env = environ.Env()
    url = "https://nufi.azure-api.net/api/v1/calcular_rfc"
    payload = {
        "nombres": "{}".format(nombres),
        "apellido_paterno": "{}".format(apellido1),
        "apellido_materno": "{}".format(apellido2),
        "fecha_nacimiento": "{}/{}/{}".format(dia, mes ,anio)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return response.text


@login_required
def calculadoraRFC(nombres, apellido1, apellido2, fnac):
    env = environ.Env()
    url = "https://nufi.azure-api.net/api/v1/calcular_rfc"
    payload = {
        "nombres": "{}".format(nombres),
        "apellido_paterno": "{}".format(apellido1),
        "apellido_materno": "{}".format(apellido2),
        "fecha_nacimiento": "{}".format(fnac)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text

#depreciado no usable
def validarINE(archivo):
    env = environ.Env()
    url = "https://api.microblink.com/v1/recognizers/blinkid"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': env('BLINKID_APIKEY')
    }

    payload = json.dumps({
        "imageSource": image_to_base64(archivo),
        "returnFullDocumentImage": True,
        "returnFaceImage": True,
        "returnSignatureImage": True,
        "imageAnalysisResult": True
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def get_blackListSAT(rfc):
    env = environ.Env()
    url = "https://nufi.azure-api.net/contribuyentes/v1/obtener_contribuyente"
    payload = {
        "rfc": "{}".format(rfc)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.text

@login_required
def get_blackListSAT2(request, rfc):
    env = environ.Env()
    url = "https://nufi.azure-api.net/contribuyentes/v1/obtener_contribuyente"
    payload = {
        "rfc": "{}".format(rfc)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": "{}".format(env('NUFI_API_KEY'))
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.text
        #print('respuesta', response.text)
        return HttpResponse(data)
    except requests.exceptions.RequestException as e:
        #print("Error en la solicitud:", e)
        return None

@login_required
def getListaNegraIntl2(request, nombrecompleto):
    env = environ.Env()
    url = "https://nufi.azure-api.net/perfilamiento/v1/aml"

    payload = {
        "nombre_completo": "{}".format(nombrecompleto),
        "primer_nombre": "",
        "segundo_nombre": "",
        "apellidos": "",
        "fecha_nacimiento": "",
        "lugar_nacimiento": ""
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "NUFI-API-KEY": "{}".format(env('NUFI_API_KEY'))
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.text
        print('respuesta', response.text)
        return HttpResponse(data)
    except requests.exceptions.RequestException as e:
        print("Error en la solicitud:", e)
        return None

@login_required
def get_reporteBuro2(request, nombre, apellido1, apellido2, rfc, fnac):
    env = environ.Env()
    url = "https://app.moffin.mx/api/v1/query/prospector_pf"
    
    payload = json.dumps({
        "birthdate": "{}".format(fnac),
        "email": "ejemplo@legalbit.com",
        "firstName": "{}".format(nombre),
        "firstLastName": "{}".format(apellido1),
        "secondLastName": "{}".format(apellido2),
        "rfc": "{}".format(rfc),
        "accountType": "PF",
        "address": "BLV. ANTONIO L. RODRIGUEZ 2100",
        "city": "MONTERREY",
        "municipality": "MONTERREY",
        "state": "NLE",
        "zipCode": "64650",
        "exteriorNumber": "2100",
        "neighborhood": "Monterrey",
        "country": "MX",
        "nationality": "MX"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': env('MOFFIN_APIKEY')
    }
    print('Ejemplo PayLoad')
    print(payload)
    print('demo', payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text




@login_required
@require_http_methods(["GET", "POST"])
def get_reporteBuro3(request, idpersona):
    if request.method == 'GET':
        persona = Personas.objects.get(id=idpersona)
        env = environ.Env()
        url = "https://app.moffin.mx/api/v1/query/prospector_pf"

        payload = {
            "birthdate": persona.fnacimiento.strftime('%Y-%m-%d'),
            "email": "ejemplo@legalbit.com",
            "firstName": persona.nombre,
            "firstLastName": persona.apellido1,
            "secondLastName": persona.apellido2,
            "rfc": persona.rfc,
            "accountType": "PF",
            "address": "BLV. ANTONIO L. RODRIGUEZ 2100",
            "city": "MONTERREY",
            "municipality": "MONTERREY",
            "state": "NLE",
            "zipCode": "64650",
            "exteriorNumber": "2100",
            "neighborhood": "Monterrey",
            "country": "MX",
            "nationality": "MX"
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': env('MOFFIN_APIKEY')
        }

        response = requests.post(url, json=payload, headers=headers)
        return JsonResponse(response.json())
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)

def get_reporteBuro(id_persona):
    persona = Personas.objects.get(id=id_persona)
    env = environ.Env()
    url = "https://app.moffin.mx/api/v1/query/prospector_pf"
    #print('fenac buro',persona.fnacimiento.strftime('%Y-%m-%d'))
    payload = json.dumps({
        "birthdate": "{}".format(persona.fnacimiento.strftime('%Y-%m-%d')),
        "email": "ejemplo@legalbit.com",
        "firstName": "{}".format(persona.nombre),
        "firstLastName": "{}".format(persona.apellido1),
        "secondLastName": "{}".format(persona.apellido2),
        "rfc": "{}".format(persona.rfc),
        "accountType": "PF",
        "address": "BLV. ANTONIO L. RODRIGUEZ 2100",
        "city": "MONTERREY",
        "municipality": "MONTERREY",
        "state": "NLE",
        "zipCode": "64650",
        "exteriorNumber": "2100",
        "neighborhood": "Monterrey",
        "country": "MX",
        "nationality": "MX"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': env('MOFFIN_APIKEY')
    }
    print('demo', payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


@login_required
def ListaInvestigaciones(request):
    qsearch = request.GET.get('txtSearch')
    selUsuario = request.GET.get('selUsuario')
    es_administrador = request.user.groups.filter(name='administrador').exists()
    user_id = request.user.id  # Obtener el ID del usuario logueado
    usuarios = User.objects.all()
    # Filtrar investigaciones por el ID del usuario logueado
    if es_administrador:
        objects_list = Investigacion.objects.all().order_by('-id')
    else:
        objects_list = Investigacion.objects.filter(usuario_id=user_id).order_by('-id')

    if selUsuario != '' and selUsuario and es_administrador:
        objects_list = Investigacion.objects.filter(usuario_id=selUsuario).order_by('-id')
    if qsearch:
        pass
        objects_list = objects_list.filter(Q(investigado__rfc__icontains=qsearch) |
                                            Q(investigado__nombre__icontains=qsearch) | 
                                            Q(investigado__apellido1__icontains=qsearch) |
                                            Q(investigado__apellido2__icontains=qsearch)).order_by('-id')
        # objects_list = objects_list.filter(Q(duenio__nombre__icontains=qsearch) | Q(duenio__rfc__icontains=qsearch))

    paginator = Paginator(objects_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'Investigaciones/Investigacion_lista.html', {'page_obj': page_obj,
                                                                        'es_admin':es_administrador,'usuarios':usuarios,
                                                                        'selUsuario': selUsuario})

@login_required
def ListaInvestigacionesPremium(request):
    qsearch = request.GET.get('txtSearch')
    selUsuario = request.GET.get('selUsuario')
    es_administrador = request.user.groups.filter(name='administrador').exists()
    user_id = request.user.id  # Obtener el ID del usuario logueado
    usuarios = User.objects.all()
    # Filtrar investigaciones por el ID del usuario logueado
    if es_administrador:
        objects_list = InvestigacionPremium.objects.all().order_by('-id')
    else:
        objects_list = InvestigacionPremium.objects.filter(usuario_id=user_id).order_by('-id')

    if selUsuario != '' and selUsuario and es_administrador:
        objects_list = InvestigacionPremium.objects.filter(usuario_id=selUsuario).order_by('-id')
    if qsearch:
        pass
        objects_list = objects_list.filter(Q(investigado__rfc__icontains=qsearch) |
                                            Q(investigado__nombre__icontains=qsearch) | 
                                            Q(investigado__apellido1__icontains=qsearch) |
                                            Q(investigado__apellido2__icontains=qsearch)).order_by('-id')
        # objects_list = objects_list.filter(Q(duenio__nombre__icontains=qsearch) | Q(duenio__rfc__icontains=qsearch))

    paginator = Paginator(objects_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'Investigaciones/premium_lista.html', {'page_obj': page_obj,
                                                                        'es_admin':es_administrador,'usuarios':usuarios,
                                                                        'selUsuario': selUsuario})




def obtener_sexo_curp(curp):
    if len(curp) >= 11:
        sexo = curp[10]
        if sexo == 'H':
            return "HOMBRE"
        elif sexo == 'M':
            return "MUJER"



@login_required
def verPDF6(request, id):
    try:
        global_username = request.user.username
        object = Investigacion.objects.get(id=id)
        if object.investigado.manual:            
            sexo = obtener_sexo_curp(object.investigado.curp)
            datascore = json.loads(object.burojson)
            score = datascore["response"]['json']['score']
             ##Entidades Int
            listanegraintl = object.listanegraintl
            listanegraintl = listanegraintl.replace("True", "true")
            listanegraintl = listanegraintl.replace("False", "false")
            listanegraintl = listanegraintl.replace("None", "null")
            listanegraintl = demjson3.decode(listanegraintl)
            entidadeslistn = listanegraintl['data']['result_payload']['sanctionlist_sources']
            sancionesintl = listanegraintl['data']['result_payload']['sanctionlist_entries']
            frame_sancionesintl = pd.json_normalize(listanegraintl['data']['result_payload']['sanctionlist_entries'],'expedientes')
            has_internationalblack = len(frame_sancionesintl)
            print('num ', has_internationalblack)
            antecedentes = demjson3.decode(object.antecedentesjson)
            situacionSAT = demjson3.decode(object.satblacklistjson.replace('None',"null"))
            #num_antecedentes = len(antecedentes['data']['resultados'])
            antecedentes2 = []
            numero_antecedentes = 0
            try:
                numero_antecedentes = int(antecedentes['data']['numero_resultados'])
                resultados_antecedentes = antecedentes['data']['resultados']
            except Exception as e:
                print(e)
            
            if numero_antecedentes > 0:
                resultados_antecedentes = antecedentes['data']['resultados']
                data_frame = pd.json_normalize(antecedentes['data']['resultados'], 'expedientes')
                buscar = "{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2)
                buscar2 = "{} {} {}".format(object.investigado.apellido1, object.investigado.apellido2, object.investigado.nombre)
                data_frame2 =  data_frame[data_frame['actor'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar)}\b', regex=True) | data_frame['actor'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar2)}\b', regex=True)]
                data_frame3 = data_frame[data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar)}\b', regex=True) | data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar2)}\b', regex=True)]
                combinado = pd.concat([data_frame2,data_frame3], ignore_index=True)
                numero_antecedentes = len(combinado)
                antecedentes2=combinado.to_dict(orient='records')
            if situacionSAT['message'] == 'No se encontró este registro dentro de los contribuyentes boletinados':
                boletinadoSAT = False
            else:
                boletinadoSAT = True
            cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
            if(cedulas_sep['code'] != 500):
                #print(cedulas_sep)
                cedulas_sep['data'] = [item for item in cedulas_sep['data'] if  unidecode(item['nombre']) == unidecode("{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2))]
                #print(cedulas_sep)
                num_cedulas = len(cedulas_sep['data'])
                resultado_cedulas = cedulas_sep['data']
            else:
                num_cedulas = 0
            ine_comentarios = demjson3.decode(object.investigado.validaine)
            print(str(ine_comentarios["data"][0]["information"]).upper())
            report = render_to_string(
                'Reports/RptInvestigacion3.html', {'object': object, 'score': int(score['value']),
                                                   'clave_elector': object.investigado.clave_elector,
                                                   'imgElector': '', 'faceINE': '',
                                                   'firmaINE': '',
                                                   'sexo': sexo,
                                                   'resultados_ant': resultados_antecedentes,
                                                   'numero_antecedentes': numero_antecedentes,
                                                   'num_cedulas': num_cedulas,
                                                   'resultado_cedulas': resultado_cedulas,
                                                   'imgElector2': '', 'mrz': object.investigado.cic_ine,
                                                   'entidadesIntl': entidadeslistn,
                                                   'sancionesIntl': sancionesintl, 'vencimientoINE': str(ine_comentarios['data'][0]['estado']).upper(),
                                                   'ine_comentarios': str(ine_comentarios['data'][0]['information']).upper(),
                                                   'folioInv': str(object.folio).zfill(5), 'situacionSAT': boletinadoSAT, 'antecedentes2': antecedentes2,
                                                   'num_antecedentes_intl': has_internationalblack

                                                   })
            params = dict(html=report)
            service = ReportService()

            result = service.render(data=params)
            return HttpResponse(base64.b64decode(result['data']), content_type='application/pdf')
        else:
            datascore = json.loads(object.burojson)

            # Acceder al valor de "score"

            score = datascore["response"]['json']['score']

            # INE
            jsonine = object.investigado.inejson
            # jsonine = str(object.investigado.inejson).replace("'", '\"')
            jsonine = jsonine.replace("True", "true")
            jsonine = jsonine.replace("False", "false")
            jsonine = jsonine.replace("None", "null")
            jsonine = demjson3.decode(jsonine)
            # print(jsonine, 'el json')
            ##json2
            jsonine2 = object.investigado.inejson2
            jsonine2 = jsonine2.replace("True", "true")
            jsonine2 = jsonine2.replace("False", "false")
            jsonine2 = jsonine2.replace("None", "null")
            jsonine2 = demjson3.decode(jsonine2)
            
            ##json2
            ##Entidades Int
            listanegraintl = object.listanegraintl
            listanegraintl = listanegraintl.replace("True", "true")
            listanegraintl = listanegraintl.replace("False", "false")
            listanegraintl = listanegraintl.replace("None", "null")
            listanegraintl = demjson3.decode(listanegraintl)
            entidadeslistn = listanegraintl['data']['result_payload']['sanctionlist_sources']
            sancionesintl = listanegraintl['data']['result_payload']['sanctionlist_entries']
            print(sancionesintl)
            ##print(entidadeslistn)
            ##Entidades ent


            # print(jsonine['response'])
            clave_elector = jsonine["data"]['ocr']['clave']
            imgElector = jsonine['data']['credencial_base64']
            imgElector2 = jsonine2['data']['credencial_base64']

            try:
                mrz = jsonine2['data']['ocr']['mrz']
                elementos = mrz.split("<<")
                if elementos:
                    # Acceder al segundo elemento
                    segundo_elemento = elementos[1]
                    mrz = segundo_elemento
                else:
                    mrz = 'MRZ Ilegible o No proporcionado por proveedor'
            except Exception as e:
                print(elementos)

            #faceINE = jsonine['result']['faceImageBase64']
            direccion_elector = jsonine["data"]['ocr']['calle_numero']
            firmaINE = ''
            vencimientoINE = jsonine["data"]['ocr']['vigencia']
            antecedentes = demjson3.decode(object.antecedentesjson)
            # entidad_ant = antecedentes['data']['resultados'][0]['entidad']
            # print( len(antecedentes['data']['resultados']))
            num_antecedentes = len(antecedentes['data']['resultados'])
            numero_antecedentes = antecedentes['data']['numero_resultados']
            resultados_antecedentes = antecedentes['data']['resultados']
            cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
            num_cedulas = len(cedulas_sep['data'])
            resultado_cedulas = cedulas_sep['data']

            # print(antecedentes['data']['resultados'][0]['entidad'])
            #html = render_to_string('Reports/InvestigationReport.html', {'object': object})
            #font_config = FontConfiguration()
            sexo = str(object.investigado.curp)[10:11]
            return render(request,
                        'Reports/RptInvestigacion.html', {'object': object, 'score': score['value'],
                                                            'clave_elector': clave_elector,
                                                            'direccionINE': direccion_elector,
                                                            'imgElector': imgElector, 'faceINE': '',
                                                            'firmaINE': firmaINE, 'vencimientoINE': vencimientoINE,
                                                            'sexo': sexo, 'num_entidadesant': num_antecedentes,
                                                            'resultados_ant': resultados_antecedentes,
                                                            'numero_antecedentes': numero_antecedentes,
                                                                'num_cedulas':num_cedulas,
                                                                'resultado_cedulas':resultado_cedulas,
                                                                'imgElector2': imgElector2, 'mrz': mrz,
                                                                'entidadesIntl': entidadeslistn,
                                                                'sancionesIntl':sancionesintl,

                                                            })
    except Exception as e:
        import traceback
        return HttpResponse('HA OCURRIDO UN ERROR, NO FUE POSIBLE GENERAR EL REPORTE <br> ERROR EN {} '.format(str(e)) + traceback.format_exc() +' ' + 
                            ' <br> <a href="/Investigaciones/Lista">Regresar</a> ')

def guardar_investigacion(data):
    try:
        # Decodificar los datos base64
        pdf_data = base64.b64decode(data)
        unique_file_id = uuid.uuid4()
        # Guardar los datos decodificados en un archivo PDF
        with open('media/mis_expedientes/{}.pdf'.format(unique_file_id), 'wb') as pdf_file:
            pdf_file.write(pdf_data)
        print('Archivo PDF guardado como "archivo.pdf"')
        return  unique_file_id, "media/mis_expedientes/{}.pdf".format(unique_file_id)
    except Exception as e:
        print(e)
        return None


@login_required
def verPDF7_html(request, id):
    try:
        object = Investigacion.objects.get(id=id)

        sexo = obtener_sexo_curp(object.investigado.curp)
        okBuroJSON = False
        score = 0
        if not object.burojson == 'ND':
            okBuroJSON = True
            datascore = json.loads(object.burojson)
            score = datascore["response"]['json']['score']
            score = int(score['value'])

        okSancionesIntl = False
        frame_sancionesintl = []
        entidadeslistn = []
        sancionesintl = []
        tablas_html = []
        has_internationalblack = 0
        if not object.listanegraintl == 'ND':
            listanegraintl = object.listanegraintl
            listanegraintl = listanegraintl.replace("True", "true")
            listanegraintl = listanegraintl.replace("False", "false")
            listanegraintl = listanegraintl.replace("None", "null")
            listanegraintl = demjson3.decode(listanegraintl)
            entidadeslistn = listanegraintl['data']['result_payload']['sanctionlist_sources']
            sancionesintl = listanegraintl['data']['result_payload']['sanctionlist_entries']
            frame_sancionesintl = pd.json_normalize(sancionesintl, 'expedientes')
            has_internationalblack = len(frame_sancionesintl)

        antecedentes2 = []
        numero_antecedentes = 0
        okAntecedentesNac = False
        resultados_antecedentes = []

        try:
            if not object.antecedentesjson == 'ND':
                okAntecedentesNac = True
                try:
                    antecedentes = demjson3.decode(object.antecedentesjson)
                    numero_antecedentes = int(antecedentes['data']['numero_resultados'])
                    resultados_antecedentes = antecedentes['data']['resultados']
                    if numero_antecedentes > 0:
                        if not antecedentes['code'] == 999:
                            data_frame = pd.json_normalize(antecedentes['data']['resultados'], 'expedientes')
                            data_frame['entidad'] = antecedentes['data']['resultados'][0]['entidad']
                            buscar = "{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2)
                            buscar2 = "{} {} {}".format(object.investigado.apellido1, object.investigado.apellido2, object.investigado.nombre)
                            data_frame3 = data_frame[
                                data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar)}\b', regex=True) |
                                data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar2)}\b', regex=True)
                            ]
                            numero_antecedentes = len(data_frame3)
                            antecedentes2 = data_frame3.to_dict(orient='records')
                            df_antecedentes2 = pd.DataFrame(antecedentes2)
                            for columna in ['acuerdos', 'tipo', 'fuero']:
                                if columna in df_antecedentes2.columns:
                                    df_antecedentes2 = df_antecedentes2.drop(columna, axis=1)
                            df_limitado = df_antecedentes2.applymap(lambda x: x[:50] if isinstance(x, str) else x)
                            trozos = [df_limitado[i:i+3] for i in range(0, len(df_limitado), 3)]
                            tablas_html = [pd.DataFrame(t).to_html(table_id='id_antecedentesNac', index=False) for t in trozos]
                        else:
                            rows = []
                            for resultado in antecedentes['data']['resultados']:
                                entidad = resultado.get('entidad', '')
                                for exp in resultado.get('expedientes', []):
                                    row = {'entidad': entidad}
                                    row.update({k: v for k, v in exp.items() if k != 'acuerdos'})
                                    rows.append(row)
                            data_frame = pd.DataFrame(rows)
                            antecedentes2 = data_frame.to_dict(orient='records')
                            numero_antecedentes = len(data_frame)
                            df_limitado = data_frame.map(lambda x: x[:50] if isinstance(x, str) else x)
                            trozos = [df_limitado[i:i+4] for i in range(0, len(df_limitado), 4)]
                            tablas_html = [pd.DataFrame(t).to_html(table_id='id_antecedentesNac', index=False) for t in trozos]
                except json.JSONDecodeError as err:
                    print('Error JSON antecedentes', err)
                    okAntecedentesNac = False
                except Exception as e:
                    print('Error antecedentes', e)
                    okAntecedentesNac = False
        except Exception as e:
            print('Error sección antecedentes', e)

        okSAT = False
        boletinadoSAT = False
        situacionSAT = False
        if not object.satblacklistjson == 'ND':
            okSAT = True
            try:
                situacionSAT = demjson3.decode(object.satblacklistjson.replace('None', "null"))
                boletinadoSAT = "No se " not in situacionSAT['message']
            except Exception as e:
                print('Error SAT', e)

        resultado_cedulas = []
        num_cedulas = 0
        okEstudios = False
        if not object.estudiosprofesionalesjson == 'ND':
            try:
                cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
                if not cedulas_sep['code'] == 999:
                    okEstudios = True
                    if cedulas_sep['code'] != 500:
                        cedulas_sep['data'] = [item for item in cedulas_sep['data'] if unidecode(item['nombre']) == unidecode("{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2))]
                        num_cedulas = len(cedulas_sep['data'])
                        resultado_cedulas = cedulas_sep['data']
                else:
                    okEstudios = True
                    num_cedulas = len(cedulas_sep['data'])
                    resultado_cedulas = cedulas_sep['data']
            except Exception as e:
                print('Error cedulas', e)

        valINE = False
        vencimiento_ine = ''
        ine_comentarios = ''
        if object.investigado.validaine not in ['.', '', None, 'ND']:
            try:
                ine_data = demjson3.decode(object.investigado.validaine)
                if ine_data.get("httpStatusCode") != 500:
                    valINE = True
                    vencimiento_ine = str(ine_data['data'][0]['estado']).upper()
                    ine_comentarios = str(ine_data['data'][0]['information']).upper()
            except Exception as e:
                print('Error INE', e)
        
        # ── Solo render, sin Playwright, sin archivos ──────────────
        return render(request, 'Reports/RptInvestigacion4.html', {
            'object': object,
            'score': score,
            'clave_elector': object.investigado.clave_elector,
            'imgElector': '', 'faceINE': '', 'firmaINE': '',
            'sexo': sexo,
            'valINE': valINE,
            'okSAT': okSAT,
            'okBuroJSON': okBuroJSON,
            'resultados_ant': resultados_antecedentes,
            'okEstudios': okEstudios,
            'okAntecedentesNac': okAntecedentesNac,
            'numero_antecedentes': numero_antecedentes,
            'num_cedulas': num_cedulas,
            'resultado_cedulas': resultado_cedulas,
            'imgElector2': '', 'mrz': object.investigado.cic_ine,
            'entidadesIntl': entidadeslistn,
            'imss_nss': '',
            'ine_comentarios': ine_comentarios,
            'sancionesIntl': sancionesintl,
            'vencimientoINE': vencimiento_ine,
            'folioInv': str(object.folio).zfill(5),
            'situacionSAT': boletinadoSAT,
            'antecedentes2': antecedentes2,
            'num_antecedentes_intl': has_internationalblack,
            'tablas_html': tablas_html,
             'base_url': request.build_absolute_uri('/')[:-1],
        })

    except Exception as e:
        import traceback
        return render(request, 'Error.html', {'error': "{} {}".format(str(e), traceback.format_exc())})


@login_required
def verPDF7(request, id):
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            context.add_cookies([{
                'name': 'sessionid',
                'value': request.COOKIES.get('sessionid'),
                'domain': request.get_host().split(':')[0],
                'path': '/',
            }])

            page = context.new_page()

            # Apunta a verPDF7_html, no a sí misma
            url = request.build_absolute_uri(f'/Investigaciones/verPDF7html/{id}')
            page.goto(url, timeout=120000)
            page.wait_for_load_state("networkidle", timeout=120000)

            pdf_bytes = page.pdf(
                format='Letter',
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            context.close()
            browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="investigacion_{id}.pdf"'
        return response

    except Exception as e:
        import traceback
        return render(request, 'Error.html', {'error': "{} {}".format(str(e), traceback.format_exc())})
    

    
@login_required
def verPDFX(request, id):
    try:
        global_username = request.user.username
        object = Investigacion.objects.get(id=id)
        print('archivo ', object.nombre_archivo)
        if object.nombre_archivo == "" or object.nombre_archivo=='ND' or object.nombre_archivo==None:
            print("ND")
            if object.investigado.manual:            
                sexo = obtener_sexo_curp(object.investigado.curp)
                okBuroJSON = False
                score = 0
                if not object.burojson == 'ND':
                    okBuroJSON = True
                    datascore = json.loads(object.burojson)
                    score = datascore["response"]['json']['score']
                    score = int(score['value'])
                ##Entidades Int
                okSancionesIntl = False
                frame_sancionesintl = []
                entidadeslistn = []
                sancionesintl= []
                tablas_html = []
                has_internationalblack = 0
                if not object.listanegraintl == 'ND':
                    okSancionesIntl = True
                    listanegraintl = object.listanegraintl
                    listanegraintl = listanegraintl.replace("True", "true")
                    listanegraintl = listanegraintl.replace("False", "false")
                    listanegraintl = listanegraintl.replace("None", "null")
                    listanegraintl = demjson3.decode(listanegraintl)
                    entidadeslistn = listanegraintl['data']['result_payload']['sanctionlist_sources']
                    sancionesintl = listanegraintl['data']['result_payload']['sanctionlist_entries']
                    frame_sancionesintl = pd.json_normalize(listanegraintl['data']['result_payload']['sanctionlist_entries'],'expedientes')
                    has_internationalblack = len(frame_sancionesintl)
                    print('num ', has_internationalblack)
                antecedentes2 = []
                numero_antecedentes = 0
                okAntecedentesNac = False
                resultados_antecedentes = []
                try:
                    if not object.antecedentesjson == 'ND':  
                            okAntecedentesNac=True
                            numero_antecedentes = 0
                            antecedentes2 = []
                            try:
                                # Parsear la cadena JSON
                                #datos_json = json.loads(object.antecedentesjson)          
                                antecedentes = demjson3.decode(object.antecedentesjson)
                                df =  pd.json_normalize(antecedentes['data']['resultados'], 'expedientes')
                                normalizado = df.to_json(lines=True, orient='records')
                                print('df ant', normalizado)
                                numero_antecedentes = int(antecedentes['data']['numero_resultados'])
                                resultados_antecedentes = antecedentes['data']['resultados']
                                antecedentes2 = []   
                                if numero_antecedentes > 0:
                                    if not antecedentes['code'] == 999:
                                        print('codigo en antecedentes', antecedentes['code'])
                                        resultados_antecedentes = antecedentes['data']['resultados']
                                        data_frame = pd.json_normalize(antecedentes['data']['resultados'], 'expedientes')
                                        # Agregar la columna 'estado' al DataFrame
                                        data_frame['entidad'] = antecedentes['data']['resultados'][0]['entidad']
                                        buscar = "{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2)
                                        buscar2 = "{} {} {}".format(object.investigado.apellido1, object.investigado.apellido2, object.investigado.nombre)
                                        #data_frame2 =  data_frame[data_frame['actor'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar)}\b', regex=True) | data_frame['actor'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar2)}\b', regex=True)]
                                        data_frame3 = data_frame[data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar)}\b', regex=True) | data_frame['demandado'].str.contains(rf'(?i)(?<!\w\s){re.escape(buscar2)}\b', regex=True)]
                                        #combinado = pd.concat([data_frame2,data_frame3], ignore_index=True)
                                        numero_antecedentes = len(data_frame3)
                                        antecedentes2=data_frame3.to_dict(orient='records')
                                        # Limitar todas las columnas a 50 caracteres
                                        # Convertir la lista a un DataFrame
                                        df_antecedentes2 = pd.DataFrame(antecedentes2)
                                        columnas_a_eliminar = ['acuerdos', 'tipo', 'fuero']
                                        for columna in columnas_a_eliminar:
                                            if columna in df_antecedentes2.columns:
                                                df_antecedentes2 = df_antecedentes2.drop(columna, axis=1)
                                                print(f"Columna '{columna}' eliminada.")
                                            else:
                                                print(f"La columna '{columna}' no existe en el DataFrame.")

                                        # Limitar todas las columnas a 50 caracteres
                                        df_limitado = df_antecedentes2.applymap(lambda x: x[:50] if isinstance(x, str) else x)

                                        max_limit = 4
                                        trozos = [df_limitado[i:i+max_limit] for i in range(0, len(df_limitado), max_limit)]
                                        # Crear tablas HTML
                                        tablas_html = []
                                        # Aplicar estilos específicos a la tabla HTML
                                        
                                        for trozo in trozos:
                                            df_trozo = pd.DataFrame(trozo)
                                            tabla_html = df_trozo.to_html(table_id='id_antecedentesNac', index=False)
                                            tablas_html.append(tabla_html)
                                    else:
                                        print('else 999')
                                        #print( antecedentes['data']['resultados'])
                                        resultados_antecedentes = antecedentes['data']['resultados']
                                        data_frame = pd.json_normalize(antecedentes['data']['resultados'], 'expedientes')
                                        # Agregar la columna 'estado' al DataFrame
                                        data_frame['entidad'] = antecedentes['data']['resultados'][0]['entidad']

                                        # Convertir a un diccionario
                                        antecedentes2 = data_frame.to_dict(orient='records')

                                        numero_antecedentes = len(data_frame)
                                        antecedentes2=data_frame.to_dict(orient='records')
                                        # Agregar la columna 'entidad' al principio del DataFrame
                                        data_frame = data_frame[['entidad'] + [col for col in data_frame.columns if col != 'entidad']]

                                        # Convertir a un diccionario
                                        antecedentes2 = data_frame.to_dict(orient='records')
                                        
                                         # Limitar todas las columnas a 50 caracteres
                                        # Convertir la lista a un DataFrame
                                        df_antecedentes2 = pd.DataFrame(antecedentes2)
                                        #df_antecedentes2 = df_antecedentes2.drop('acuerdos',axis=1)
                                        #df_antecedentes2 = df_antecedentes2.drop('tipo',axis=1)
                                        #df_antecedentes2 = df_antecedentes2.drop('fuero',axis=1)

                                        # Limitar todas las columnas a 50 caracteres
                                        df_limitado = df_antecedentes2.applymap(lambda x: x[:50] if isinstance(x, str) else x)

                                        max_limit = 4
                                        trozos = [df_limitado[i:i+max_limit] for i in range(0, len(df_limitado), max_limit)]
                                        # Crear tablas HTML
                                        tablas_html = []
                                        # Aplicar estilos específicos a la tabla HTML
                                        
                                        for trozo in trozos:
                                            df_trozo = pd.DataFrame(trozo)
                                            tabla_html = df_trozo.to_html(table_id='id_antecedentesNac', index=False)
                                            tablas_html.append(tabla_html)


                            except json.JSONDecodeError as err:
                                print('Error al procesar, el archivo no tiene la estructura correcta', err)
                                okAntecedentesNac=False
                                object.antecedentesjson = 'ND'
                            except Exception as e:
                                print('error ', e)
                                traceback.print_exc()
                                okAntecedentesNac=False
                                  

                except Exception as e:
                    print('Error sección antecedentes', e)
                okSAT = False
                boletinadoSAT = False
                situacionSAT = False
                if not object.satblacklistjson == 'ND':
                    okSAT = True
                    try:
                        situacionSAT = demjson3.decode(object.satblacklistjson.replace('None',"null"))
                    except Exception as e:
                        print('Error sección blacklist sat', e)
                    print('SITACION SAT', situacionSAT['message'])
                
                    if "No se " in situacionSAT['message']:
                        boletinadoSAT = False
                    else:
                        boletinadoSAT = True
                    print('boletinado', boletinadoSAT)
                resultado_cedulas = []
                num_cedulas = 0
                okEstudios = False
                if not object.estudiosprofesionalesjson == 'ND':
                    
                        try:
                            cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
                            if not cedulas_sep['code'] == 999:
                                okEstudios = True
                                cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
                                if(cedulas_sep['code'] != 500):
                                    #print(cedulas_sep)
                                    cedulas_sep['data'] = [item for item in cedulas_sep['data'] if  unidecode(item['nombre']) == unidecode("{} {} {}".format(object.investigado.nombre, object.investigado.apellido1, object.investigado.apellido2))]
                                    #print(cedulas_sep)
                                    num_cedulas = len(cedulas_sep['data'])
                                    resultado_cedulas = cedulas_sep['data']
                                else:
                                    num_cedulas = 0
                                    resultado_cedulas = []
                            else:
                                try:
                                    okEstudios = True
                                    cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
                                    num_cedulas = len(cedulas_sep['data'])
                                    resultado_cedulas = cedulas_sep['data']
                                except Exception as e:
                                    print(e)
                        except Exception as e:
                            print(e)
                    
                    
                
                valINE = False
                if object.investigado.validaine == '.':
                    vencimiento_ine = ''
                    ine_comentarios = ''
                elif object.investigado.validaine == '':
                    vencimiento_ine = ''
                    ine_comentarios = ''
                elif object.investigado.validaine == None:
                    vencimiento_ine = ''
                    ine_comentarios = ''
                elif object.investigado.validaine == 'ND':
                    vencimiento_ine = ''
                    ine_comentarios = ''
                else:
                    ine_comentarios = demjson3.decode(object.investigado.validaine)
                    http_status_code = ine_comentarios.get("httpStatusCode")

                    if http_status_code == 500:
                        valINE = False
                        vencimiento_ine = ''
                        ine_comentarios = ''
                    else:
                        valINE = True                    
                        ine_validada = str(ine_comentarios['data'][0]['estado']).upper()
                        vencimiento_ine = str(ine_comentarios['data'][0]['estado']).upper()
                        ine_comentarios = str(ine_comentarios['data'][0]['information']).upper()
                print('uuid imss',object.investigado.uuid_imss) 
                response_imss = []
                #if reponses.objects.filter(transaction_id=object.investigado.uuid_imss).exists():
                #    response_imss = reponses.objects.get(transaction_id=object.investigado.uuid_imss).data
                #    response_imss = response_imss.replace("'",'"')
                #    response_imss = response_imss.replace("True","true")
                #    response_imss = response_imss.replace("False","false")
                #if response_imss is not None:
                #    print(response_imss)
                #    imss_json = json.loads(response_imss)
                #    nss_imss = imss_json['nss']
                #    #print('demjson imss', imss_json,'NSS', nss_imss)
                #    historial_imss = imss_json['data']['historialLaboral']
                #    print('Historial ', historial_imss)
                #else:
                #    nss_imss = ''
                #    imss = []
                #    historial_imss = []
                #report = render_to_string(
                #    'Reports/RptInvestigacion4.html', {'object': object, 'score': score,
                #                                    'clave_elector': object.investigado.clave_elector,
                #                                    'imgElector': '', 'faceINE': '',
                #                                    'firmaINE': '',
                #                                    'sexo': sexo,
                #                                    'valINE': valINE,
                #                                   'okSAT': okSAT,
                #                                    'okBuroJSON':okBuroJSON,
                #                                    #'imss_data':imss_json,
                #                                    #'historial_imss' : historial_imss,
                #                                    'resultados_ant': resultados_antecedentes,
                #                                   'okEstudios':okEstudios,
                #                                    'numero_antecedentes': numero_antecedentes,
                #                                    'num_cedulas': num_cedulas,
                #                                    'resultado_cedulas': resultado_cedulas,
                #                                   'imgElector2': '', 'mrz': object.investigado.cic_ine,
                #                                    'entidadesIntl': entidadeslistn,
                #                                    'imss_nss': '',
                #                                    'ine_comentarios': ine_comentarios,
                #                                    'sancionesIntl': sancionesintl, 'vencimientoINE': vencimiento_ine,
                #                                    'folioInv': str(object.folio).zfill(5), 'situacionSAT': boletinadoSAT, 'antecedentes2': antecedentes2,
                #                                    'num_antecedentes_intl': has_internationalblack,
                #                                    'tablas_html':tablas_html,
                #                                    })
                #try:
                #    params = dict(html=report)
                #    service = ReportService()
                #    result = service.render(data=params)
                #    nombre_uuid, nombre_file = guardar_investigacion(result['data'])
                #    object.nombre_archivo = "ND"
                #    object.save()
                #    categoria =  CategoriaExpedientes.objects.get(id=1)
                #    expediente = Expedientes(expediente_categoria_id=categoria)
                #    expediente.usuario_id = request.user.id
                #   expediente.cliente_id = object.investigado.id
                #    archivo_contenido = open(object.nombre_archivo, 'rb').read()
                #    #Crear un objeto ContentFile con el contenido del archivo
                #    archivo_content_file = ContentFile(archivo_contenido)
                #    expediente.expediente_nombre.save("{}.pdf".format(nombre_uuid), archivo_content_file)
                #    expediente.save()
                #    print('expediente_guardado')
                #except Exception as e:
                #    print('ocurrio un error al guardar el PDF ', e)

                return render(request,
                    'Reports/RptInvestigacion4.html',{'object': object, 'score': score,
                                                    'clave_elector': object.investigado.clave_elector,
                                                    'imgElector': '', 'faceINE': '',
                                                    'firmaINE': '',
                                                    'sexo': sexo,
                                                    'valINE': valINE,
                                                    'okSAT': okSAT,
                                                    'okBuroJSON':okBuroJSON,
                                                    #'imss_data':imss_json,
                                                    #'historial_imss' : historial_imss,
                                                    'resultados_ant': resultados_antecedentes,
                                                    'okEstudios':okEstudios,
                                                    'okAntecedentesNac': okAntecedentesNac,
                                                    'numero_antecedentes': numero_antecedentes,
                                                    'num_cedulas': num_cedulas,
                                                    'resultado_cedulas': resultado_cedulas,
                                                    'imgElector2': '', 'mrz': object.investigado.cic_ine,
                                                    'entidadesIntl': entidadeslistn,
                                                    'imss_nss': '',
                                                    'ine_comentarios': ine_comentarios,
                                                    'sancionesIntl': sancionesintl, 'vencimientoINE': vencimiento_ine,
                                                    'folioInv': str(object.folio).zfill(5), 'situacionSAT': boletinadoSAT, 'antecedentes2': antecedentes2,
                                                   'num_antecedentes_intl': has_internationalblack,
                                                    'tablas_html':tablas_html,
                                                    })
                #print(result['data'])
                #return HttpResponse(base64.b64decode(result['data']), content_type='application/pdf')
                #return render(request,
                #           'Reports/RptInvestigacion4.html', {'object': object, 'score': score['value'],
                #                                      'clave_elector': object.investigado.clave_elector,
                #                                      'imgElector': '', 'faceINE': '',
                #                                      'firmaINE': '',
                #                                      'sexo': sexo,
                #                                      #'imss_data':imss_json,
                #                                      #'historial_imss' : historial_imss,
                #                                      'resultados_ant': resultados_antecedentes,
                #                                       'numero_antecedentes': numero_antecedentes,
                #                                       'num_cedulas': num_cedulas,
                #                                       'resultado_cedulas': resultado_cedulas,
                #                                       'imgElector2': '', 'mrz': object.investigado.cic_ine,
                #                                       'entidadesIntl': entidadeslistn,
                #                                       'imss_nss': '',
                #                                        'ine_comentarios': str(ine_comentarios['data'][0]['information']).upper(),
                #                                       'sancionesIntl': sancionesintl, 'vencimientoINE': str(ine_comentarios['data'][0]['estado']).upper(),
                #                                      'folioInv': str(object.folio).zfill(5), 'situacionSAT': boletinadoSAT, 'antecedentes2': antecedentes2,
                #                                       'num_antecedentes_intl': has_internationalblack
                # 
                #                                       })
            else:
                datascore = json.loads(object.burojson)

                # Acceder al valor de "score"

                score = datascore["response"]['json']['score']

                # INE
                jsonine = object.investigado.inejson
                # jsonine = str(object.investigado.inejson).replace("'", '\"')
                jsonine = jsonine.replace("True", "true")
                jsonine = jsonine.replace("False", "false")
                jsonine = jsonine.replace("None", "null")
                jsonine = demjson3.decode(jsonine)
                # print(jsonine, 'el json')
                ##json2
                jsonine2 = object.investigado.inejson2
                jsonine2 = jsonine2.replace("True", "true")
                jsonine2 = jsonine2.replace("False", "false")
                jsonine2 = jsonine2.replace("None", "null")
                jsonine2 = demjson3.decode(jsonine2)
                
                ##json2
                ##Entidades Int
                listanegraintl = object.listanegraintl
                listanegraintl = listanegraintl.replace("True", "true")
                listanegraintl = listanegraintl.replace("False", "false")
                listanegraintl = listanegraintl.replace("None", "null")
                listanegraintl = demjson3.decode(listanegraintl)
                entidadeslistn = listanegraintl['data']['result_payload']['sanctionlist_sources']
                sancionesintl = listanegraintl['data']['result_payload']['sanctionlist_entries']
                print(sancionesintl)
                ##print(entidadeslistn)
                ##Entidades ent


                # print(jsonine['response'])
                clave_elector = jsonine["data"]['ocr']['clave']
                imgElector = jsonine['data']['credencial_base64']
                imgElector2 = jsonine2['data']['credencial_base64']

                try:
                    mrz = jsonine2['data']['ocr']['mrz']
                    elementos = mrz.split("<<")
                    if elementos:
                        # Acceder al segundo elemento
                        segundo_elemento = elementos[1]
                        mrz = segundo_elemento
                    else:
                        mrz = 'MRZ Ilegible o No proporcionado por proveedor'
                except Exception as e:
                    print(elementos)

                #faceINE = jsonine['result']['faceImageBase64']
                direccion_elector = jsonine["data"]['ocr']['calle_numero']
                firmaINE = ''
                vencimientoINE = jsonine["data"]['ocr']['vigencia']
                antecedentes = demjson3.decode(object.antecedentesjson)
                # entidad_ant = antecedentes['data']['resultados'][0]['entidad']
                # print( len(antecedentes['data']['resultados']))
                num_antecedentes = len(antecedentes['data']['resultados'])
                numero_antecedentes = antecedentes['data']['numero_resultados']
                resultados_antecedentes = antecedentes['data']['resultados']
                cedulas_sep = demjson3.decode(object.estudiosprofesionalesjson)
                num_cedulas = len(cedulas_sep['data'])
                resultado_cedulas = cedulas_sep['data']

                # print(antecedentes['data']['resultados'][0]['entidad'])
                #html = render_to_string('Reports/InvestigationReport.html', {'object': object})
                #font_config = FontConfiguration()
                sexo = str(object.investigado.curp)[10:11]
                return render(request,
                            'Reports/RptInvestigacion.html', {'object': object, 'score': score['value'],
                                                                'clave_elector': clave_elector,
                                                                'direccionINE': direccion_elector,
                                                                'imgElector': imgElector, 'faceINE': '',
                                                                'firmaINE': firmaINE, 'vencimientoINE': vencimientoINE,
                                                                'sexo': sexo, 'num_entidadesant': num_antecedentes,
                                                                'resultados_ant': resultados_antecedentes,
                                                                'numero_antecedentes': numero_antecedentes,
                                                                    'num_cedulas':num_cedulas,
                                                                    'resultado_cedulas':resultado_cedulas,
                                                                    'imgElector2': imgElector2, 'mrz': mrz,
                                                                    'entidadesIntl': entidadeslistn,
                                                                    'sancionesIntl':sancionesintl,

                                                                })
        else:
            try:
                return FileResponse(open(object.nombre_archivo, 'rb'), content_type='application/pdf')
            except Exception as e:
                print(e)
    except Exception as e:
        import traceback
        return render(request,'Error.html', {'error':"{} {}".format(str(e), traceback.format_exc())})

@login_required
def getAntecedentesNacionalesAPI(request, id):
    try:
        # Obtén la instancia del modelo
        #mi_objeto = Investigacion.objects.get(id=296)
        persona = Personas.objects.get(id=id)
        # Obtiene el contenido del campo antecedentesjson
        #antecedentes = mi_objeto.antecedentesjson
        
        #print(ant['data'])
        antecedentes =  obtenerAntecedentes(persona.nombre, persona.apellido1, persona.apellido2)
        ant =  demjson3.decode(antecedentes)
        df = pd.json_normalize(ant['data'])
       
        normalizado = df.to_json(lines=True, orient='records')
        # Retorna una respuesta HTTP con el contenido como texto plano
        return HttpResponse(normalizado, content_type='text/plain')
    except Investigacion.DoesNotExist:
        # Manejar la excepción si el objeto no existe
        return HttpResponse('No hay datos disponibles', content_type='text/plain')
    
@login_required
def getAntecedentesNacionalesAPI2(request, nombre, apellido1,apellido2):
    try:
        # Obtén la instancia del modelo
        #mi_objeto = Investigacion.objects.get(id=296)
        #persona = Personas.objects.get(id=id)
        # Obtiene el contenido del campo antecedentesjson
        #antecedentes = mi_objeto.antecedentesjson
        
        #print(ant['data'])
        antecedentes =  obtenerAntecedentes(nombre, apellido1, apellido2)
        #ant =  demjson3.decode(antecedentes)
        #df = pd.json_normalize(ant['data'])
       
        #normalizado = df.to_json(lines=True, orient='records')
        # Retorna una respuesta HTTP con el contenido como texto plano
        return HttpResponse(antecedentes, content_type='text/plain')
    except Investigacion.DoesNotExist:
        # Manejar la excepción si el objeto no existe
        return HttpResponse('No hay datos disponibles', content_type='text/plain')
    

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Investigacion, Personas

@csrf_exempt
@login_required
def postAPIIniciarInvestigacion2(request):
    if request.method == 'POST':
        try:
            datos_json = json.loads(request.body.decode('utf-8'))
            print('JSON Investigacion 2')
            print(datos_json)

            # Verificar si las claves existen en el diccionario antes de acceder a ellas
            personaid = datos_json.get("persona", None)
            if personaid is None:
                raise KeyError('La clave "persona" no está presente en los datos JSON')

            # Obtener la persona
            objPersona = Personas.objects.get(id=personaid)
            print('Persona id' , personaid)

            antecedentes_nac = datos_json.get("ant", None)
            buro = datos_json.get("buro", None)
            intl = datos_json.get("intl", None)
            sat = datos_json.get("sat", None)

            investigacion = Investigacion()
            investigacion.usuario = request.user
            investigacion.nombre_archivo='ND'
            investigacion.estudiosprofesionalesjson = 'ND'
            investigacion.antecedentesjson = antecedentes_nac
            investigacion.investigado = objPersona
            investigacion.burojson = buro
            investigacion.listanegraintl = intl
            investigacion.satblacklistjson = sat
            investigacion.save()
            print('Investigacion ID:', investigacion.id)

            # Devolver una respuesta JSON
            respuesta = {'id': investigacion.id}
            return JsonResponse(respuesta)
        except KeyError as ke:
            print('Error al iniciar investigación: Clave no encontrada:', ke)
            return JsonResponse({'error': 'Clave no encontrada en los datos JSON'}, status=400)
        except Personas.DoesNotExist:
            print('Error al iniciar investigación: La persona no existe')
            return JsonResponse({'error': 'La persona no existe'}, status=400)
        except Exception as e:
            print('Error al iniciar investigación:', e)
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@csrf_exempt 
@login_required
def postAPIGuardarPremium(request):
    if request.method == 'POST':
        datos = json.loads(request.body.decode('utf-8'))
        print('Datos recibidos', datos)
        obj = InvestigacionPremium()
        principal = datos.get('principal', None)
        conyugue = datos.get('conyugue', None)
        padreArrendatario = datos.get('padreArrendatario', None)
        madreArrendatario = datos.get('madreArrendatario', None)
        padreConyugue = datos.get('padreConyugue', None)
        madreConyugue = datos.get('madreConyuge', None)
        aval = datos.get('aval', None)
        obj.principal = Investigacion.objects.get(id=principal)
        obj.usuario = request.user
        
        if conyugue:
            obj.conyugue = Investigacion.objects.get(id=conyugue)
        if padreArrendatario:
            obj.padre_principal = Investigacion.objects.get(id=padreArrendatario)
        if madreArrendatario:
            obj.madre_principal = Investigacion.objects.get(id=madreArrendatario)
        if  padreConyugue:
            obj.padre_conyugue= Investigacion.objects.get(id=padreConyugue)
        if madreConyugue:
            obj.madre_conyugue =Investigacion.objects.get(id=madreConyugue)
        if  aval :
            obj.aval = Investigacion.objects.get(id=aval)
        
        try:
            obj.save()
            respuesta = {'id': obj.id}
            return JsonResponse(respuesta)
        except Exception as e:
            print('Error ', e)
    
    
@csrf_exempt
@login_required
def postAPIIniciarInvestigacion(request):
    if request.method == 'POST':
        user_id = request.user.id
        get_user_config = ConfiguracionUsuariosLB.objects.get(usuario_id=user_id)
        num_investigaciones = Investigacion.objects.filter(usuario_id=user_id).count()
        if num_investigaciones <= get_user_config.max_investigaciones: 
            # Obtener los datos JSON del cuerpo de la solicitud
            datos_json = json.loads(request.body.decode('utf-8'))

            # Ahora, 'datos_json' contiene los datos que fueron enviados desde el cliente

            # Hacer algo con los datos (por ejemplo, imprimirlos)
            print("Datos recibidos:", datos_json)
            personaid = datos_json.get("idPersona", None)
            objPersona = Personas.objects.get(id=personaid)
            investigacion = Investigacion()
            antecedentes_nac =  datos_json.get("antecedentes", None)
            investigacion.estudiosprofesionalesjson = 'ND'
            estudios = datos_json.get('estudios', None)
            investigacion.estudiosprofesionalesjson = estudios
            investigacion.nombre_archivo = "ND"
            investigacion.investigado = objPersona
            investigacion.aprobado = True
            burojson = 'ND'
            score = '0'
            try:
                burojson = get_reporteBuro(objPersona.id)
                resburo = demjson3.decode(burojson)
                if 'statusCode' in resburo and resburo['statusCode'] is not None:
                    if resburo['statusCode'] == 400 or resburo['statusCode'] == 401 or resburo['statusCode'] == 403:
                        errores = errores + "<br> Error al conectar a la API Buró {}".format(resburo['message'])
                        datascore = json.loads(investigacion.burojson)
                        score = datascore["response"]['json']['score']['value']
            except Exception as e:
                        print(e)

            investigacion.burojson = burojson
            investigacion.listanegraintl = 'ND'
            satblack = 'ND'
            try:
                blackListSAT = get_blackListSAT(objPersona.rfc)
                blackSATJSON = demjson3.decode(blackListSAT)
                satblack = blackListSAT
            except Exception as e:
                print(e)
            investigacion.satblacklistjson = satblack
            investigacion.folio= Investigacion.objects.last().folio + 1
            investigacion.antecedentesjson = antecedentes_nac
            investigacion.notas = ''
            
            investigacion.usuario = request.user
            investigacion.save()
            print('persona', datos_json.get("idPersona", None))

            # Puedes devolver una respuesta JSON si es necesario
            respuesta = {'id': investigacion.id}
            return JsonResponse(respuesta)
        else:
            # Manejar otros métodos HTTP si es necesario
            return JsonResponse({'mensaje': 'error'}, status=405)

@login_required
def getEstudiosProfesionalesAPI(request,id):
    try:
        # Obtén la instancia del modelo
        #mi_objeto = Investigacion.objects.get(id=296)
        persona = Personas.objects.get(id=id)
        #cedulas = mi_objeto.estudiosprofesionalesjson
        cedulas = obtenerHistorialAcademico(persona.nombre, persona.apellido1, persona.apellido2)
        # Retorna la respuesta JSON utilizando JsonResponse
        return JsonResponse({'cedulasprof': cedulas})
    except Investigacion.DoesNotExist:
        # Manejar la excepción si el objeto no existe
        return JsonResponse({'error': 'No hay datos disponibles'})
    
@login_required
def antecedentesToExcel(request, id):
    data_frame = pd.DataFrame()
    try:
        obj = Investigacion.objects.get(id=id)
        if not obj.antecedentesjson == 'ND':
            datos = demjson3.decode(obj.antecedentesjson)
            try:
                data_frame = pd.json_normalize(datos['data']['resultados'], 'expedientes')
            except Exception as e:
                print(e)
        # Crear un objeto BytesIO para almacenar el archivo Excel en memoria
        excel_file = BytesIO()
        data_frame.to_excel(excel_file, engine='openpyxl', index=False)
        excel_file.seek(0)

        # Configurar la respuesta HTTP para el archivo Excel
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=antecedentes.xlsx'

        return response
    except Investigacion.DoesNotExist:
        # Manejar la excepción si el objeto no existe
        return JsonResponse({'error': 'No hay datos disponibles'})
    
@login_required
def api_renapo(curp):
     env = environ.Env()
     url = "https://app.moffin.mx/api/v1/query/renapo_curp"
     payload = json.dumps({
           "curp": "{}".format(curp),
            "accountType": "PF"
        })
     headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': env('MOFFIN_APIKEY')
        }

     response = requests.request("POST", url, headers=headers, data=payload)
     return response.json()

@login_required
def preguntas(request):
    return render(request,'Investigaciones/preguntas.html',{})


@login_required
def VerPDFPremium(request):
    return render(request,'Reports/RptInvestigacionPremium.html',{})
    

@login_required
@require_POST
def reload_INEVal(request, id):
    # 1. Obtener el tipo desde el POST (enviado por el formulario o fetch)
    tipo = request.POST.get("tipo")  # o desde JSON si usas fetch con JSON

    if not tipo:
        return HttpResponseBadRequest("Falta el parámetro 'tipo'")

    # 2. Obtener la investigación
    try:
        investigacion = Investigacion.objects.get(id=id)
    except Investigacion.DoesNotExist:
        return HttpResponseBadRequest("Investigación no encontrada")

    # 3. Obtener la persona (ajusta esto según tu modelo)
    # Si tu modelo Investigacion tiene un FK a Persona:
    # persona = investigacion.persona
    try:
        persona = Personas.objects.get(id=investigacion.investigado.id)
    except Personas.DoesNotExist:
        return HttpResponseBadRequest("Persona no encontrada")

    # 4. Llamar a tu función de validación
    persona.validaine = validaListaNominal2(
        tipo,
        persona.cic_ine,
        persona.identificador_ine,
    )
    persona.save()

    # 5. Redirigir de vuelta a la lista
    return HttpResponseRedirect('/Investigaciones/Lista')


def _parse_multi_json(raw_text):
    decoder = json.JSONDecoder()
    objects = []
    idx = 0
    raw_text = raw_text.strip()
    while idx < len(raw_text):
        while idx < len(raw_text) and raw_text[idx] in ' \t\n\r':
            idx += 1
        if idx >= len(raw_text):
            break
        obj, end_idx = decoder.raw_decode(raw_text, idx)
        objects.append(obj)
        idx = end_idx
    return objects


INSTITUCIONES_KEYWORDS = [
    'INSTITUTO', 'JUZGADO', 'MINISTERIO', 'FISCAL', 'PODER',
    'SECRETARIA', 'INFONAVIT', 'FONDO', 'NACIONAL', 'TRABAJADORES',
    'CONSEJO', 'JUDICATURA', 'TRIBUNAL', 'DIRECCION', 'GOBIERNO'
]


def _es_institucion(nombre):
    nombre_upper = nombre.upper()
    return any(kw in nombre_upper for kw in INSTITUCIONES_KEYWORDS)


def _extraer_nombre_investigado(perfil_data):
    listas = [
        perfil_data.get('Demandas_Civiles_Detalles', []),
        perfil_data.get('Demandas_Familiares_Detalles', []),
        perfil_data.get('Demandas_Penales_Detalles', []),
        perfil_data.get('Demandas_Administrativas_Detalles', []),
        perfil_data.get('Demandas_Laborales_Detalles', []),
    ]
    for lista in listas:
        for demanda in lista:
            demandado = demanda.get('Demandado', '').strip()
            actor = demanda.get('Actor', '').strip()
            if demandado and not _es_institucion(demandado):
                return demandado
            if actor and not _es_institucion(actor):
                return actor
    return ''


def _build_burojson(perfil_data, credito_data, nombre='', apellido1=''):
    rfc = perfil_data.get('RFC', '').split(' ')[0].strip()
    curp = perfil_data.get('CURP', '')
    score_raw = str(credito_data.get('score_crediticio', '0'))
    score_value = score_raw.split('/')[0].strip()
    colonia = perfil_data.get('Colonia', '')

    return {
        "id": None,
        "uuid": None,
        "authentication": "IMPORTADO",
        "service": "prospector_pf",
        "status": "SUCCESS",
        "state": None,
        "metadata": {
            "clientType": "PF",
            "reportType": "prospector_pf",
            "query": {
                "rfc": rfc,
                "curp": curp,
                "email": "importado@legalbit.mx",
                "phone": None,
                "address": colonia,
                "country": "MX",
                "birthdate": None,
                "firstName": nombre,
                "firstLastName": apellido1,
                "secondLastName": "",
                "accountType": "PF",
                "nationality": "MX",
            }
        },
        "response": {
            "json": {
                "name": {
                    "firstname": nombre,
                    "firstLastname": apellido1,
                    "secondLastname": "",
                    "rfc": rfc,
                    "nationality": "MX"
                },
                "score": {
                    "name": "BC SCORE",
                    "code": "007",
                    "value": score_value.zfill(4),
                    "cause1": "",
                    "cause2": "",
                    "cause3": ""
                },
                "address": {
                    "address": colonia,
                    "neighborhood": "",
                    "municipality": "",
                    "city": "",
                    "state": "",
                    "zipCode": ""
                },
                "header": {"wasFound": "1"}
            }
        },
        "credito_original": credito_data,
        "perfil_original": perfil_data,
    }


def _build_antecedentesjson(perfil_data):
    from collections import defaultdict

    grupos = defaultdict(list)

    all_demandas = (
        perfil_data.get('Demandas_Civiles_Detalles', []) +
        perfil_data.get('Demandas_Familiares_Detalles', []) +
        perfil_data.get('Demandas_Penales_Detalles', []) +
        perfil_data.get('Demandas_Administrativas_Detalles', []) +
        perfil_data.get('Demandas_Laborales_Detalles', [])
    )

    for d in all_demandas:
        entidad = d.get('Estado', 'Sin Estado')
        grupos[entidad].append({
            "expediente": d.get('Expediente', ''),
            "demandado":  d.get('Demandado', ''),
            "actor":      d.get('Actor', ''),
            "juzgado":    d.get('Instancia', ''),
            "fecha":      d.get('Fecha_presentacion', ''),
            "acuerdos":   {}
        })

    resultados = [
        {"entidad": entidad, "expedientes": exps}
        for entidad, exps in grupos.items()
    ]

    return {
        "code": 999,
        "status": "success",
        "message": "Consulta exitosa",
        "data": {
            "numero_resultados": len(resultados),
            "resultados": resultados
        }
    }


@login_required
def ImportarExterno(request):
    from Generales.models import Estados, Municipios, Colonia

    if request.method == 'GET':
        return render(request, 'Investigaciones/importar_externo.html', {})

    uploaded_file = request.FILES.get('json_file')
    if not uploaded_file:
        return render(request, 'Investigaciones/importar_externo.html', {
            'error': 'Debes seleccionar un archivo .json',
        })

    try:
        raw = uploaded_file.read().decode('utf-8')
        objects = _parse_multi_json(raw)

        credito_data = next((o for o in objects if 'score_crediticio' in o and 'pagos_totales' in o), {})
        perfil_data  = next((o for o in objects if 'RFC' in o and 'CURP' in o and any(k.startswith('Demandas_') for k in o)), {})

        rfc_clean   = str(perfil_data.get('RFC') or perfil_data.get('Rfc') or perfil_data.get('rfc') or '').split(' ')[0].strip()
        curp        = str(perfil_data.get('CURP') or perfil_data.get('Curp') or perfil_data.get('curp') or '').strip()
        nss         = str(perfil_data.get('NSS') or perfil_data.get('Nss') or perfil_data.get('nss') or '').strip()
        colonia_str = str(perfil_data.get('Colonia') or perfil_data.get('colonia') or '').strip()

        nombre_completo = _extraer_nombre_investigado(perfil_data).strip()
        partes = [p for p in nombre_completo.split(' ') if p]
        if len(partes) >= 2:
            nombre    = partes[0]
            apellido1 = ' '.join(partes[1:])
        elif len(partes) == 1:
            nombre    = partes[0]
            apellido1 = ''
        else:
            nombre    = ''
            apellido1 = ''
        apellido2   = ''
        razonsocial = nombre_completo or rfc_clean

        burojson_built         = _build_burojson(perfil_data, credito_data, nombre=nombre, apellido1=apellido1)
        antecedentesjson_built = _build_antecedentesjson(perfil_data)

        estadocivil   = EstadosCiviles.objects.first()
        lugarnac      = LugarNacimientoCURP.objects.first()
        clave_estado  = curp[11:13].upper() if len(curp) >= 13 else ''
        estado_obj    = Estados.objects.filter(clave__iexact=clave_estado).first()
        if not estado_obj:
            nombre_estado = next((
                d.get('Estado', '') for lista in [
                    perfil_data.get('Demandas_Civiles_Detalles', []),
                    perfil_data.get('Demandas_Familiares_Detalles', []),
                    perfil_data.get('Demandas_Penales_Detalles', []),
                    perfil_data.get('Demandas_Administrativas_Detalles', []),
                    perfil_data.get('Demandas_Laborales_Detalles', []),
                ] for d in lista if d.get('Estado')
            ), '')
            estado_obj = Estados.objects.filter(estado__icontains=nombre_estado).first() if nombre_estado else None
        if not estado_obj:
            estado_obj = Estados.objects.first()
        municipio_obj = Municipios.objects.first()
        colonia_obj   = Colonia.objects.first()

        persona = Personas.objects.create(
            rfc=rfc_clean or 'XXXX000000XXX',
            curp=curp or 'XXXX000000XXXXXX00',
            razonsocial=razonsocial,
            nombre=nombre,
            apellido1=apellido1,
            apellido2=apellido2,
            calle=colonia_str,
            uuidnss=nss,
            tipo='PF',
            manual=True,
            correo_electronico='importado@legalbit.mx',
            telefono_principal='0000000000',
            estadocivil=estadocivil,
            lugarNacimiento=lugarnac,
            estado=estado_obj,
            municipio=municipio_obj,
            colonia=colonia_obj,
            usuario=request.user,
            
        )

        last_inv = Investigacion.objects.last()
        folio = (last_inv.folio + 1) if (last_inv and last_inv.folio) else 1001

        investigacion = Investigacion.objects.create(
            investigado=persona,
            burojson=json.dumps(burojson_built, ensure_ascii=False),
            antecedentesjson=json.dumps(antecedentesjson_built, ensure_ascii=False),
            satblacklistjson='ND',
            listanegraintl='ND',
            nombre_archivo=f'Importado_{rfc_clean}_{date.today()}',
            folio=folio,
            usuario=request.user,
            notas='REXT:Importado desde JSON externo',
        )

        return render(request, 'Investigaciones/importar_externo.html', {
            'success': True,
            'investigacion': investigacion,
            'persona': persona,
        })

    except Exception as e:
        import traceback
        return render(request, 'Investigaciones/importar_externo.html', {
            'error': f'Error procesando el archivo: {str(e)}\n\n{traceback.format_exc()}',
        })
