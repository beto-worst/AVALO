""" Django Q tasks for 'MisCobranzas' app
    In admin panel, under DJANGO Q > Scheduled tasks, create a new task with the following parameters:
    Doted path: MisCobranzas.tasks.<function_name>
    Args: <frequency> (daily, weekly, monthly, biannual)
    Adjust the time to run the task according to the frequency
"""
import environ
from django.utils import timezone
from django.core.mail import EmailMessage
from twilio.rest import Client
from . models import get_phone, CobranzasMessages  # NotificationChoice, FrequencyChoice, client_list,

env = environ.Env()


def twilio_client():
    """get twilio client"""
    account_sid = env('TWILIO_ACCOUNT_SID')
    auth_token = env('TWILIO_AUTH_TOKEN')
    return Client(account_sid, auth_token)


def get_messages(notification, frequency):
    """get a list of messages by broker_id, notification, frequency"""
    return CobranzasMessages.objects.filter(Notification=notification, Frequency=frequency, status=True).all()


def send_mail(frequency):
    """send email messages"""
    if email_messages := get_messages("mail", frequency):
        for email_message in email_messages:
            try:
                EmailMessage(f'{email_message.email_subject}', f'{email_message.body}', to=[f'{email_message.Client.correo_electronico}']).send()
            except Exception as e:
                print(f"{e}: not sent")
            else:
                CobranzasMessages.objects.filter(pk=email_message.pk).update(delivered=True, updated=timezone.now())
                print(f'{frequency} EMAIL message sent to: {email_message.Client.correo_electronico}')
    else:
        print('No EMAIL messages to send')
    print('EMAIL task completed')
    return None


def send_sms(frequency):
    """send sms messages"""
    from_phone = env('TWILIO_SMS')
    if sms_messages := get_messages("sms", frequency):
        for sms_message in sms_messages:
            try:
                client_id = sms_message.Client.pk
                to_phone = get_phone(client_id)
                # to_phone = f'+52{to_phone}'
                to_phone = f'+58{to_phone}' if to_phone.startswith('412') else f'+52{to_phone}'
                message = twilio_client().messages.create(from_=from_phone, body=sms_message.body, to=to_phone)
            except Exception as e:
                print(f"{e}: not sent")
            else:
                CobranzasMessages.objects.filter(pk=sms_message.pk).update(delivered=True, updated=timezone.now())
                print(f'{frequency} SMS message sent to: {to_phone}, ssid: {message.sid}')
    else:
        print('No SMS messages to send')
    print('SMS task completed')
    return None


def send_voice(frequency):
    """send voice messages"""
    from_phone = env('TWILIO_SMS')
    if voice_messages := get_messages("llamar", frequency):
        for voice_message in voice_messages:
            try:
                client_id = voice_message.Client.pk
                to_phone = get_phone(client_id)
                # to_phone = f'+52{to_phone}'
                to_phone = f'+58{to_phone}' if to_phone.startswith('412') else f'+52{to_phone}'
                message = twilio_client().calls.create(from_=from_phone, twiml=f'<Response><Say>{voice_message.body}</Say></Response>', to=to_phone)
            except Exception as e:
                print(f"{e}: not sent")
            else:
                CobranzasMessages.objects.filter(pk=voice_message.pk).update(delivered=True, updated=timezone.now())
                print(f'{frequency} voice message sent to: {to_phone}, ssid: {message.sid}')
    else:
        print('No Voice messages to send')
    print('Voice task completed')
    return None


def send_whatsapp(frequency):
    """send whatsapp messages"""
    from_phone = env('TWILIO_WHATSAPP')
    if whatsapp_messages := get_messages("whatsapp", frequency):
        for whatsapp_message in whatsapp_messages:
            try:
                client_id = whatsapp_message.Client.pk
                to_phone = get_phone(client_id)
                # to_phone = f'whatsapp:+52{to_phone}'
                to_phone = f'whatsapp:+58{to_phone}' if to_phone.startswith('412') else f'whatsapp:+52{to_phone}'
                message = twilio_client().messages.create(from_=from_phone, body=whatsapp_message.body, to=to_phone)
            except Exception as e:
                print(f"{e}: not sent")
            else:
                CobranzasMessages.objects.filter(pk=whatsapp_message.pk).update(delivered=True, updated=timezone.now())
                print(f'{frequency} WhatsApp message sent to: {to_phone}, ssid: {message.sid}')
    else:
        print('No WhatsApp messages to send')
    print('WhatsApp task completed')
    return None