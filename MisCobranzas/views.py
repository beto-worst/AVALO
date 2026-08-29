import environ
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from . models import NotificationChoice, FrequencyChoice, CobranzasMessages, client_list, client, collection_templates, collection_lst, get_folios
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt

env = environ.Env()


# Create your views here.
@login_required(login_url="login")
def index(request):

    broker = request.user
    n_choices = NotificationChoice.choices
    n_frequency = FrequencyChoice.choices
    client_lst = client_list(broker)
    cobranzas_template = collection_templates(broker)
    messages_lst = collection_lst(broker)
    broker = request.user
    is_htmx = request.htmx

    context = {
        'notification_choices': n_choices,
        'frequency_choices': n_frequency,
        'client_list': client_lst,
        'cobranzas_template': cobranzas_template,
        'messages_lst': messages_lst,
        'is_htmx': is_htmx,
    }

    if request.htmx:
        is_htmx = request.htmx
        if request.method == 'GET':
            if client_id := request.GET.get('client'):
                contract_lst = get_folios(broker.id, int(client_id))
                context['contract_lst'] = contract_lst
            context['is_htmx'] = is_htmx

            return render(request, 'MisCobranzas/partials/htmx_contracts_select.html', context)

        elif request.method == 'POST':
            client_id = request.POST.get('client')
            contract = request.POST.get('contract')
            frequency = request.POST.get('frequency')
            notification = request.POST.get('notification')
            body = request.POST.get('body')
            status = bool(request.POST.get('status'))

            # For multiple template choices in the database update this section
            client_info = client(client_id)
            email_subj = cobranzas_template[0].name_subject
            body = body.replace('{{nombre}}', client_info.nombre).replace('{{apellido1}}', client_info.apellido1).replace('{{contract}}', contract)

            # insert into database
            CobranzasMessages.objects.create(
                Broker=broker,
                Client_id=client_id,
                email_subject=email_subj,
                Notification=notification,
                Frequency=frequency,
                folio=contract,
                body=body,
                status=status
            )

            return render(request, 'MisCobranzas/partials/htmx_index_partial.html', context)

    return render(request, 'MisCobranzas/index.html', context)


@login_required(login_url="login")
def update_status(request, pk, scheduled_status):
    """update status by id"""
    if request.htmx:
        msg_status = bool(request.GET.get('scheduled_status'))
        CobranzasMessages.objects.filter(id=pk).update(status=msg_status)  # move to model as a function
        return HttpResponse('')  # returns status status=200
    return HttpResponse('error')


@login_required(login_url="login")
def delete_message(request, pk):
    """delete a message by id"""
    if request.htmx:
        messages_lst = collection_lst(request.user)
        CobranzasMessages.objects.filter(id=pk).delete()  # move to model as a function
        context = {
            'messages_lst': messages_lst,
        }
        return render(request, 'MisCobranzas/partials/htmx_schedule_partial.html', context)
    return HttpResponse('error')


# ------- Twilio Webhook -------
@csrf_exempt
def status_callback(request):
    # Retrieve message status details from the request
    message_sid = request.POST.get('MessageSid')
    message_status = request.POST.get('MessageStatus')

    with open('readme.txt', 'w') as f:
        f.write(f'SID: {message_sid}, Status: {message_status}')

    # Log or process the message status as needed
    print(f"Message SID: {message_sid}, Status: {message_status}")

    # Optional: Respond to Twilio with a TwiML message
    resp = MessagingResponse()
    resp.message("Message status received successfully.")
    return HttpResponse(str(resp))


# webhook and get messages from twilio
# https://www.twilio.com/docs/messaging/tutorials/how-to-receive-and-reply/python
# forwar sms to cell phone
# https://stackoverflow.com/a/74881122/6202092