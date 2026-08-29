from django.db import models
from django.contrib.auth.models import User
from Documentos.models import Archivos, FormatosDocumento
from MisExpedientes.models import Expedientes, CategoriaExpedientes
from Personas.models import Personas


# Create your models here.
class CoordinateTemplates(models.Model):
    doc_format = models.ForeignKey(FormatosDocumento, on_delete=models.DO_NOTHING)
    template_name = models.CharField(max_length=150, unique=True, blank=True, null=True)
    template_description = models.TextField(blank=True, null=True)
    template_json = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.doc_format}/{self.template_name}"


class WtContracts(models.Model):
    contract_id = models.ForeignKey(Archivos, on_delete=models.DO_NOTHING)
    wt_contract_id = models.CharField(max_length=150, unique=True, blank=True, null=True)
    broker = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    client = models.ForeignKey(Personas, on_delete=models.DO_NOTHING)
    wt_status = models.CharField(max_length=150, blank=True, null=True)
    wt_doc_link = models.TextField(blank=True, null=True)
    wt_returned_json = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class WtSignatures(models.Model):
    wt_contract = models.CharField(max_length=150, unique=True, blank=True, null=True)
    broker = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    arrendador_email = models.EmailField(max_length=150, blank=True, null=True)
    arrendador_name = models.CharField(max_length=150, blank=True, null=True)
    observador_email = models.EmailField(max_length=150, blank=True, null=True)
    observador_name = models.CharField(max_length=150, blank=True, null=True)
    arrendatario_email = models.EmailField(max_length=150, blank=True, null=True)
    arrendatario_name = models.CharField(max_length=150, blank=True, null=True)
    email_title = models.CharField(max_length=150, blank=True, null=True)
    email_message = models.TextField(blank=True, null=True)
    nickname = models.CharField(max_length=150, blank=True, null=True)
    wt_signatory_json = models.TextField(blank=True, null=True)
    wt_json_response = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class WtWebhooks(models.Model):
    wt_contract = models.ForeignKey(WtContracts, on_delete=models.DO_NOTHING)
    hook_type = models.CharField(max_length=150, blank=True, null=True)
    hook_status = models.CharField(max_length=150, blank=True, null=True)
    documentURL = models.TextField(blank=True, null=True)
    certificateURL = models.TextField(blank=True, null=True)
    pscCertificateURL = models.TextField(blank=True, null=True)
    hook_json = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


def get_clients(user_id):
    """ get a list of clients by user_id (broker) """
    return Archivos.objects.filter(usuario=user_id).distinct().values('id', 'uuid_archivo', 'persona', 'persona__nombre', 'persona__apellido1', 'persona__apellido2', 'persona__correo_electronico')


# Using "archivos" write a function to get the documents for a client
def get_client_documents(client_id):
    """ get a list of documents by client_id """
    return Archivos.objects.filter(id=client_id).distinct().values('id', 'uuid_archivo')


# Get document uuid_archivo from Archivos by id
def get_document_uuid(doc_id):
    """ get a document uuid_archivo by doc_id """
    return Archivos.objects.filter(id=doc_id).values('uuid_archivo')[0]['uuid_archivo']


def get_archive_instance(archive_id):
    """ get an archive instance by archive_id """
    return Archivos.objects.get(id=archive_id)


def get_client_instance(client_id):
    """ get a client instance by client_id """
    return Personas.objects.get(id=client_id)