from django.urls import path
from . import views

app_name='Investigaciones'
urlpatterns = [

    path('', views.index, name='index'),
    path('', views.validaRenapo, name='validaRENAPO'),
    path('NuevoHome', views.nuevo_home, name='Nuevo Home'),
    path('IniciarInvestigacion', views.iniciarInvestigacion, name='Iniciar Investigación'),
    path('Lista', views.ListaInvestigaciones, name='Investigaciones'),
     path('PremiumList', views.ListaInvestigacionesPremium, name='Investigaciones Premium'),
    path('EscaneoINE', views.escaneo_index, name='Escaneo INE'),
    path('verPDF6/<int:id>', views.verPDF6, name='PDF 6'),
     path('verPDF7/<int:id>', views.verPDF7, name='PDF7'),
    path('verPDF7html/<int:id>', views.verPDF7_html, name='PDF7html'),
     path('verPDFX/<int:id>', views.verPDFX, name='PDF X'),
    path('agregarPersona', views.agregarPersona, name='InvAddPersona'),
    path("AgregarPersonaM", views.addPersonaManual, name="AgregarPersonaM"),
    path('InvestigacionManual', views.InvestigadoManual, name= 'Investigacion Manual'),
    path('ObtenerDatosxCURP/<str:curp>', views.obtenerDatosCURP, name= 'Obtener Datos a travez de la CURP'),
    path('ObtenerDatosxCURP2/<str:curp>', views.obtenerDatosCURP2, name= 'Obtener Datos a travez de la CURP'),
    path('CalculadoraRFC/<str:nombres>/<str:apellido1>/<str:apellido2>/<str:dia>/<str:mes>/<str:anio>', views.calculadoraRFC2, name= 'CalcularRFC'),
    path('GenerarCURP/<str:entidad>/<str:dia>/<str:mes>/<str:nombre>/<str:apellido1>/<str:apellido2>/<str:anio>/<str:sexo>', views.calcularCURP, name= 'CalcularRFC'),
    path('ValidaINEListaNominal/<str:tipo>/<str:cic>/<str:identificador>', views.validaListaNominal, name= 'Validar Lista Nominal'),
    path('getJSONAntecedentesNacionales/<int:id>',views.getAntecedentesNacionalesAPI, name='API antecedentes'),
    path('getJSONAntecedentesNacionales2/<str:nombre>/<str:apellido1>/<str:apellido2>',views.getAntecedentesNacionalesAPI2, name='API antecedentes'),
    path('getBUROJSON/<str:nombre>/<str:apellido1>/<str:apellido2>/<str:rfc>/<str:fnac>',views.get_reporteBuro2, name='API BURO 2'),
    path('getBUROJSON2/<int:idpersona>',views.get_reporteBuro3, name='API BURO 2'),
    path('getJSONEstudiosProfesionales/<int:id>',views.getEstudiosProfesionalesAPI, name='API Cedulas'),
    path('APIiniciarInvestigacion',views.postAPIIniciarInvestigacion, name='API INiciar inv'),
    path('APIiniciarInvestigacion2',views.postAPIIniciarInvestigacion2, name='API INiciar inv 2'),
    path('APISavePremium', views.postAPIGuardarPremium, name='API Save Premium'),
    path('getExcel/<int:id>',views.antecedentesToExcel, name='API Cedulas'),
    path('Cuestionario',views.preguntas, name='Cuestionario'),
    path('Premium',views.index_investigacion_premium, name='InvestigaciónPremium'),
    path('PDFPremium', views.VerPDFPremium, name='PDFPremium'),
    path('addPersonaAPI', views.addPersonaAPI, name='addPersonaAPI'),
    path('getSAT/<str:rfc>', views.get_blackListSAT2, name='Blacklist sat API'),
    path('getListaInt/<str:nombrecompleto>', views.getListaNegraIntl2, name='Blacklist sat API'),
    path('reload_ine/<int:id>', views.reload_INEVal, name='reload_ine'),
    path('ImportarExterno/', views.ImportarExterno, name='ImportarExterno'),
     #calcularCURP(request,entidad,dia,mes,nombre,apellido1,apellido2,anio,sexo):
]
