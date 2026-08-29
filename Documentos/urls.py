from django.urls import path
from . import views

app_name='Documentos'
urlpatterns = [

    path('TiposDocumento', views.TiposDocumento_List.as_view(), name='index'),
    path('NuevoArrendamiento', views.NuevoArrendamiento, name='index'),
    path('NuevoPrestacionServicios', views.index_prestacion_serv, name='Nuevo prestación de servicios'),
    path('TiposDocumento/add', views.TiposDocumento_Add.as_view(), name='Agregar Tipo Documento'),
    path('TiposDocumento/edit/<int:pk>', views.TiposDocumento_Edit.as_view(), name='Tipos Documento Edit'),
    path('TiposDocumento/delete/<int:pk>', views.TiposDocumento_Delete.as_view(), name='EstadosDelete'),
    path('GeneraDocArrendamiento', views.generarDocumento, name='genara arrendamiento'),
    path('MisDocumentos', views.index_misdocumentos, name='Mis Documentos Index'),
    path('GeneraDocServicios', views.generaDocServicios, name='Mis Documentos Index'),
    path('DescargarDocumentoPDF/<str:name>', views.descargar_documentoPDF, name='Descargar Documento'),
    path('DescargarDocumentoDOCX/<str:name>', views.descargar_documentoDOCX, name='Descargar Documento'),
    path('GeneraGarantia', views.gen_garantia_index, name='Gen Garantia Index'),
    path('', views.index2, name='EstadosDelete'),
]