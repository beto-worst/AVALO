import time
import environ
from . models import UserPayment, UserPaymentHistory, Products
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import json
import stripe

env = environ.Env()
stripe.api_key = env('STRIPE_SECRET_KEY')


def create_stripe_customer(request):
    try:
        customer = stripe.Customer.create(
            name=request.user.first_name + ' ' + request.user.last_name,
            email=request.user.email,
            tax_exempt='exempt',
            preferred_locales=['es'],
        )
        return customer
    except Exception as e:
        raise e


def update_stripe_customer(request, stripe_cus_id):
    try:
        customer = stripe.Customer.modify(
            stripe_cus_id,
            name=request.user.first_name + ' ' + request.user.last_name,
            email=request.user.email,
            preferred_locales=['es'],
        )
        return customer
    except Exception as e:
        raise e


def delete_stripe_customer(request):
    try:
        stripe_cus_id = UserPayment.objects.get(user=request.user).stripe_customer_id
        customer = stripe.Customer.delete(
            stripe_cus_id,
        )
        # Delete user from UserPayment table
        UserPayment.objects.get(user=request.user).delete()
        # cascade to new table: UserPaymentHistory
        return customer
    except Exception as e:
        raise e


def checkout_session_crate(request, price_id, quantity=1):
    try:
        print('Checkut session')
        checkout_session = stripe.checkout.Session.create(
            #customer=UserPayment.objects.get(user=request.user).stripe_customer_id,
            payment_method_types=['card'],
            currency='MXN',
            locale='es',
            #line_items=[{
            #    #'price': Products.objects.get(id=price_id).stripe_price_id,
            #    'price': 100,
            #    'quantity': quantity,
            #}],
            line_items=[{
                'price_data': {
                    'currency': 'MXN',
                    'product_data': {
                        'name': Products.objects.get(id=price_id).name,  # Nombre del producto
                    },
                    'unit_amount': int(Products.objects.get(id=price_id).price * 100),  # Precio en centavos
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url=env('STRIPE_REDIRECT_UR') + '/Credito/payment_successful/?session_id={CHECKOUT_SESSION_ID}' + '&pid=' + price_id,
            cancel_url=env('STRIPE_REDIRECT_UR') + '/Credito/payment_canceled',
        )
        return checkout_session
    except Exception as e:
        print('error en payment')
        print(e)
        raise e
       


# Create your views here.
@login_required(login_url='login')
def index(request):
    # product_list = Products.objects.all()
    # all the products with a status of True
    product_list = Products.objects.filter(status=True)
    product_list = product_list.order_by('name')
    if UserPayment.objects.filter(user=request.user).exists():
        user_payment_id = UserPayment.objects.get(user=request.user).id
        payment_history = UserPaymentHistory.objects.filter(user_payment_id=user_payment_id).order_by('-date_updated')
        context = {'product_list': product_list,
                   'payment_history': payment_history}
    else:
        context = {'product_list': product_list}

    if request.htmx:
        if request.method == 'GET':
            user_payment_id = UserPayment.objects.get(user=request.user).id
            payment_history = UserPaymentHistory.objects.filter(user_payment_id=user_payment_id).order_by('-date_updated')
            context = {'product_list': product_list,
                       'payment_history': payment_history}
            return render(request, 'CargarCredito/partials/htmx_reload_transactions.html', context)

    if request.method == 'POST':
        prod_qty = request.POST.get('quantity')
        price_id = request.POST.get('price_id')
        print('el id enviado es ', price_id)
    # Check if user has a stripe_customer_id in UserPayment table update email, if not create one and add to UserPayment table.
        if UserPayment.objects.filter(user=request.user).exists():
            stripe_cus_id = UserPayment.objects.get(user=request.user).stripe_customer_id
            update_stripe_customer(request, stripe_cus_id)
        else:
            customer = create_stripe_customer(request)
            stripe_cus_id = customer.id
            user_payment = UserPayment(user=request.user, stripe_customer_id=stripe_cus_id)
            user_payment.save()
        # Create a checkout session
        checkout_session = checkout_session_crate(request, price_id, prod_qty)
        return redirect(checkout_session.url, code=303)

    return render(request, 'CargarCredito/index.html', context)


@login_required(login_url='login')
def product_select(request):
    if request.htmx:
        product_list = Products.objects.filter(status=True)
        product_list = product_list.order_by('name')
        context = {'product_list': product_list}
        if request.method == 'GET':
            if price_id := request.GET.get('price_id', None):
                if price_id == '4':
                    set_qt = 1
                elif price_id == '3':
                    set_qt = 30
                elif price_id == '6':
                    set_qt = 101
                elif price_id == '7':
                    set_qt = 301
                else:
                    set_qt = 0
                context['selected_qt'] = set_qt
                return render(request, 'CargarCredito/partials/htmx_qt_update.html', context)
            # return render(request, 'CargarCredito/partials/htmx_qt_update.html', context)

            if quantity := request.GET.get('quantity', None):
                quantity = int(quantity)
                print(quantity)
                if quantity > 0 and quantity <= 29:
                    selected_product = 4
                elif quantity >= 30 and quantity <= 100:
                    selected_product = 3
                elif quantity >= 101 and quantity <= 300:
                    selected_product = 6
                elif quantity >= 301:
                    selected_product = 7
                else:
                    selected_product = 0
                context['selected_product'] = selected_product
                return render(request, 'CargarCredito/partials/htmx_prod_update.html', context)
    return HttpResponse("Por favor escriba un número mayor que 0")  # send partial view


@login_required(login_url='login')  # 4242 4242 4242 4242
def payment_successful(request):
    price_id = request.GET.get('pid', None)
    product_name = Products.objects.get(id=price_id).name
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    up_id = UserPayment.objects.get(stripe_customer_id=customer.id)
    # Check if checkout_session_id is allready in the database
    if UserPaymentHistory.objects.filter(stripe_checkout_id=checkout_session_id).exists():
        return redirect("CargarCredito:index")
        # return HttpResponse('<h1> That checkout session ID is allready in the Database </h>', status=200)
    else:
        UserPaymentHistory(user_payment_id=up_id, stripe_checkout_id=checkout_session_id, plan=product_name).save()
    return redirect("CargarCredito:index")
    # return render(request, 'CargarCredito/payment_sucessful.html')


@login_required(login_url='login')
def payment_canceled(request):
    return redirect("CargarCredito:index")
    # return render(request, 'CargarCredito/payment_canceled.html', {})


@csrf_exempt
def stripe_webhook(request):
    if request.method == 'POST':
        time.sleep(10)
        payload = request.body
        endpoint_secret = env('STRIPE_WEBHOOK_SECRET')
        sig_header = request.headers.get('Stripe-Signature')
        try:
            # We are looking for the event
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            print(e)
            return JsonResponse({'error': str(e)})
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return JsonResponse({'error': str(e)})

        if event.type == 'payment_intent.created':
            payment_intent = event.data.object  # contains a stripe.PaymentIntent
            print('PaymentIntent was created! ' + payment_intent.id)
            print('status: ' + payment_intent.status)

        if event.type == 'checkout.session.completed':
            session = event.data.object  # contains a stripe.PaymentIntent
            session_id = session.id
            session_amount = (session.amount_total / 100)
            time.sleep(15)
            print('Checkout session compleated! ' + session.id)
            payment_history = UserPaymentHistory.objects.get(stripe_checkout_id=session_id)
            payment_history.payment_bool = True
            payment_history.amount = session_amount
            payment_history.save()

            print(event.type)
            print(type(event.data.object))
            print(session_id)
            print(session_amount)
            print(event.data.object)

        return JsonResponse({'status': 'success'})
    return HttpResponse('<h1>GO AWAY</h>', status=400)


@login_required(login_url='login')
def delete_customer(request):
    delete_stripe_customer(request)
    return HttpResponse("Customer deleted")