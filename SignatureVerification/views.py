import time
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . wt_conn import add_document, fixed_coordinates, delete_document, request_signature, resend_signature
from . models import get_clients, get_client_documents, CoordinateTemplates, get_document_uuid, WtContracts, WtSignatures, WtWebhooks, get_archive_instance, get_client_instance
from . wt_formatting_tools import fixed_signatory_generator, update_signatory_array, create_signature_request
import json

@login_required(login_url='login')
def index(request):
    client_lst = get_clients(request.user.id)
    # get contracts from WtContracts with request.user
    contracts_lst = WtContracts.objects.filter(broker=request.user).order_by('-id')
    signature_info = WtSignatures.objects.filter(broker=request.user)
    # get all the urls from WtWebhooks where broker in WtSignatures
    if compleated_urls := WtWebhooks.objects.filter(wt_contract__broker=request.user, hook_type='completedDocument').values('wt_contract__wt_contract_id', 'documentURL', 'certificateURL', 'pscCertificateURL'):
        compleated_urls = list(compleated_urls)
    else:
        compleated_urls = []

    context = {
        "compleated_urls": compleated_urls,  # type: ignore
        "signature_info": signature_info,
        "contracts": contracts_lst,
        "clients": client_lst,
    }
    if request.htmx:
        if request.method == 'POST':
            observer_email = request.POST.get('observer_email')
            observer_name = request.POST.get('observer_name')
            email_title = request.POST.get('email_title')
            email_message = request.POST.get('email_message')
            client_select = request.POST.get('client_select')
            contract_select = request.POST.get('contract_select')
            # broker = request.user.id
            contract_uuid = get_document_uuid(contract_select)
            contract_path = f"media/mis_expedientes/{contract_uuid}.pdf"
            wt_upload = add_document(contract_path)

            if wt_upload[1] == 200:
                data = wt_upload[0]['responseData']  # type: ignore
                wt_id = data['documentID']  # type: ignore
                wt_status = data['status']  # type: ignore
                wt_url = data['documentFileObj']['url']  # type: ignore
                wt_returned_json = json.dumps(data)  # type: ignore

                # add to WtContracts
                WtContracts.objects.create(
                    contract_id=get_archive_instance(contract_select),
                    wt_contract_id=wt_id,
                    broker=request.user,
                    client=get_client_instance(client_select),
                    wt_status=wt_status,
                    wt_doc_link=wt_url,
                    wt_returned_json=wt_returned_json
                )

                client = get_client_instance(client_select)
                arrendatario_email = client.correo_electronico
                arrendatario_name = client.nombre + " " + client.apellido1

                arrendador_email = request.POST.get('arrendador_email')
                arrendador_name = request.POST.get('arrendador_name')

                fsg_emails = {
                    "arrendatario": f"{arrendatario_email}",
                    "arrendador": f"{arrendador_email}",
                }

                # Fix signatory coordinates to contract
                coo_templ = CoordinateTemplates.objects.get(pk=1).template_json
                fsg = fixed_signatory_generator(wt_id, json.loads(coo_templ), fsg_emails)
                fixed_coordinates(fsg)

                # Create signature request and save to WtSignatures
                nickname = f"{client.apellido1}-{contract_uuid[-8:]}"
                signature_array = update_signatory_array(arrendatario_email, arrendatario_name, "arrendatario", arrendador_email, arrendador_name, "arrendador", nickname)
                signature_json = create_signature_request(signature_array, wt_id, nickname, email_message, email_title, observer_email)

                # Add to WtSignatures
                WtSignatures.objects.create(
                    wt_contract=wt_id,
                    broker=request.user,
                    arrendador_email=arrendador_email,
                    arrendador_name=arrendador_name,
                    observador_email=observer_email,
                    observador_name=observer_name,
                    arrendatario_email=arrendatario_email,
                    arrendatario_name=arrendatario_name,
                    email_title=email_title,
                    email_message=email_message,
                    nickname=nickname,
                    wt_signatory_json=json.dumps(signature_json)
                )

                return render(request, 'SignatureVerification/partials/htmx_index_partial.html', context)
    return render(request, 'SignatureVerification/index.html', context)


@login_required(login_url='login')
def index_htmx_form(request):
    if request.htmx:
        if request.method == 'POST':
            client_id = request.POST.get('client_select')
            if client_id == "":
                client_id = 'x'
            if client_id != 'x':
                doc_lst = get_client_documents(client_id)
                # select the last five characters of the uuid_archivo
                for doc in doc_lst:
                    doc['uuid_archivo'] = doc['uuid_archivo'][-8:]
            else:
                doc_lst = 'x'

            context = {
                "contract_lst": doc_lst,
            }
            return render(request, 'SignatureVerification/partials/htmx_contract_select.html', context)
    context = {
        # "clients": client_lst,
    }
    return render(request, 'SignatureVerification/partials/htmx_contract_select.html', context)


@login_required(login_url='login')
def delete_contract(request):
    if request.htmx:
        if request.method == 'POST':
            contracts_lst = WtContracts.objects.filter(broker=request.user).order_by('-id')
            signature_info = WtSignatures.objects.filter(broker=request.user)
            if compleated_urls := WtWebhooks.objects.filter(wt_contract__broker=request.user, hook_type='completedDocument').values('wt_contract__wt_contract_id', 'documentURL', 'certificateURL', 'pscCertificateURL'):
                compleated_urls = list(compleated_urls)
            else:
                compleated_urls = []

            wtc_id = request.POST.get('wtc_id')
            wt_contract_id = request.POST.get('wt_contract_id')
            delete_respose = delete_document(wt_contract_id)
            if delete_respose[1] == 200:
                contract_del_db = WtContracts.objects.get(pk=int(wtc_id))
                contract_del_db.delete()
                # delete from WtSignatures
                signature_del_db = WtSignatures.objects.get(wt_contract=wt_contract_id)
                signature_del_db.delete()
            context = {
                "compleated_urls": compleated_urls,  # type: ignore
                "signature_info": signature_info,
                "contracts": contracts_lst,
            }
            return render(request, 'SignatureVerification/partials/htmx_doc_list.html', context)
    return render(request, 'SignatureVerification/partials/htmx_index_partial.html')


@login_required(login_url='login')
def verify(request):
    contracts_lst = WtContracts.objects.filter(broker=request.user).order_by('-id')
    signature_info = WtSignatures.objects.filter(broker=request.user)
    if compleated_urls := WtWebhooks.objects.filter(wt_contract__broker=request.user, hook_type='completedDocument').values('wt_contract__wt_contract_id', 'documentURL', 'certificateURL', 'pscCertificateURL'):
        compleated_urls = list(compleated_urls)
    else:
        compleated_urls = []

    # wtc_id = request.POST.get('wtc_id')
    wt_contract_id = request.POST.get('wt_contract_id')
    wts_json = WtSignatures.objects.get(wt_contract=wt_contract_id).wt_signatory_json
    req_signature = request_signature(json.loads(wts_json))  # type: ignore
    if req_signature[1] == 200:
        data = req_signature[0]['responseData']  # type: ignore
        wt_id = data['documentID']  # type: ignore
        wt_status = data['status']  # type: ignore
        # update WtContracts with wt_status where wt_contract_id = wt_id
        contract_update = WtContracts.objects.get(wt_contract_id=wt_id)
        contract_update.wt_status = wt_status
        # update WtSignatures with wt_json_response where wt_contract = wt_id
        returned_json = json.dumps(data)  # type: ignore
        signature_update = WtSignatures.objects.get(wt_contract=wt_id)
        signature_update.wt_json_response = returned_json
        contract_update.save()
        signature_update.save()

    context = {
        "compleated_urls": compleated_urls,  # type: ignore
        "signature_info": signature_info,
        "contracts": contracts_lst,
    }
    return render(request, 'SignatureVerification/partials/htmx_doc_list.html', context)


@login_required(login_url='login')
def resend_verification(request):
    if request.htmx:
        if request.method == 'POST':
            contracts_lst = WtContracts.objects.filter(broker=request.user).order_by('-id')
            signature_info = WtSignatures.objects.filter(broker=request.user)
            if compleated_urls := WtWebhooks.objects.filter(wt_contract__broker=request.user, hook_type='completedDocument').values('wt_contract__wt_contract_id', 'documentURL', 'certificateURL', 'pscCertificateURL'):
                compleated_urls = list(compleated_urls)
            else:
                compleated_urls = []

            context = {
                        "compleated_urls": compleated_urls,  # type: ignore
                        "signature_info": signature_info,
                        "contracts": contracts_lst,
                    }

            wt_contract_id = request.POST.get('wt_contract_id')
            resend = resend_signature(wt_contract_id)
            if resend[1] == 200:
                message = resend[0]['message']  # type: ignore
                context['rv_message'] = message

    return render(request, 'SignatureVerification/partials/htmx_doc_list.html', context)


# --- webhooks ---
@csrf_exempt
def webhook(request):
    # extract type, status, and date. Then save object to database
    try:
        data = json.loads(request.body)
        response_type = data['type']
        wtc_id = data['Document']['documentID']
        response_status = data['Document']['status']
        print(wtc_id, response_type, response_status)
        print()
        print(data)

        if response_type == 'completedDocument':
            # save to WtWebhooks
            WtWebhooks.objects.create(
                wt_contract=WtContracts.objects.get(wt_contract_id=wtc_id),
                hook_type=response_type,
                hook_status=response_status,
                documentURL=data['Document']['documentURL'],
                certificateURL=data['Document']['certificateURL'],
                pscCertificateURL=data['Document']['pscCertificateURL'],
                hook_json=json.dumps(data)
            )
            # update WtContracts with wt_status where wt_contract_id = wtc_id
            contract_update = WtContracts.objects.get(wt_contract_id=wtc_id)
            contract_update.wt_status = response_status
            contract_update.save()
        else:
            # save to WtWebhooks
            WtWebhooks.objects.create(
                wt_contract=WtContracts.objects.get(wt_contract_id=wtc_id),
                hook_type=response_type,
                hook_status=response_status,
                hook_json=json.dumps(data)
            )
            contract_update = WtContracts.objects.get(wt_contract_id=wtc_id)
            contract_update.wt_status = response_status
            contract_update.save()

        print(response_type, response_status)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return HttpResponse('')
