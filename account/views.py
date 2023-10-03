# standard library
import random
import uuid  # For generating unique identifiers
from decimal import Decimal
from datetime import date , datetime

# Django
from django.shortcuts import render , redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage ,send_mail
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth.decorators import login_required

# thrid party
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.forms import PayPalPaymentsForm
from decouple import config

# local Django
from .models import User , Transaction , CouponUsage
from adminpanel.models import CoinsPack, Coupon

def signUp(request):
    # retreive details from post
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        otp = str(random.randint(100000, 999999))  #generating otp
        
        # storing details in session 
        request.session['otp'] = otp        
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        
        message = f"OTP verification Process. Your otp is : {otp}"
        subject = 'Otp verification'
        from_email = config('EMAIL_ADD')
        to_email = [email]
        send_mail(subject,message,from_email , to_email)
        
        return redirect('verify-otp')
    return render(request , 'account/accountsignup.html')

def verifyOtp(request):
    if request.method =="POST":
        stored_otp = request.session.get('otp')
        user_otp = request.POST['otp']
        if user_otp == stored_otp:
            stored_username = request.session.get('username')
            stored_email = request.session.get('email')
            stored_password = request.session.get('password')
            user = User.objects.create_user(username=stored_username,email=stored_email,password=stored_password)
            del request.session['otp']
            del request.session['email']
            del request.session['password']
            return redirect('acc-signin')
        else:
            del request.session['otp']
            del request.session['email']
            del request.session['password']
            return render(request, 'account/verify_otp.html', {'error': 'Invalid OTP'})     
    return render(request , 'account/verify_otp.html')


def signIn(request):
    # eget details for login
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']  
        # authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'account/accountsignin.html', {'error_message': 'Invalid credentials'})
    return render(request , 'account/accountsignin.html')
            
            
@login_required(login_url='/account/signin/')
def payment(request , packId):
    error = None
    coupon_offer = 0
    
    # retreive pack details
    pack = CoinsPack.objects.get(id = packId)
    details = {}
    
    # if coupon
    if request.method == "POST":
        coupon = request.POST.get('coupon')
        
        # coupon validations
        try:
            coupon = Coupon.objects.get(code=coupon)
            # wheather already used or not 
            if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
                print('coupon already used')
                error = 'Coupon already used'
                
            # check expiry date
            elif coupon.expiration_date < date.today():
                print('Coupon Expired')
                error = 'Coupon Expired'
            
            # check if acitve or not
            elif coupon.active == False :
                print('coupon is inactive')
                error = 'Coupon is Inactive'
            
            # use coupon after all validation
            else:
                request.session['coupon_id'] = coupon.id
                coupon_offer = coupon.discount
                you_save = float(((Decimal(coupon_offer) / Decimal(100)) * Decimal(pack.price_after_offer)))
                details['you_save'] = you_save
                details['coupon_offer'] = coupon_offer
 
        except Coupon.DoesNotExist:
            error = 'Check you code again'
            print("Coupon does not exist")
        
    # details for passing to paypal gateway  
    item_name = f"Pack of {pack.coins} coins"
    unique_invoice_id = uuid.uuid4().hex   
    request.session['in_id'] = unique_invoice_id
    request.session['pack_id'] = packId
    # amount = 0
    
    amount = float(Decimal(pack.price_after_offer) - ((Decimal(coupon_offer) / Decimal(100)) * Decimal(pack.price_after_offer)))
    print(amount)
    request.session['amount'] = amount
    
    # paypal requirements
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL ,
        "amount": amount,
        "item_name": item_name ,
        "invoice": unique_invoice_id,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('payment-completed')),
        "cancel_return": request.build_absolute_uri(reverse('payment-failed')),
    }
    
    # paypal forms
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "form": form,
        'coinpack' : pack,
        'amount' : amount,
        'error' : error,
        'details' : details
        }
    return render(request , 'account/payment.html' , context)


def payment_completed_view(request): 
    # searching the sesssion
    if request.session.get('pack_id') and request.session.get('in_id'):
        
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        amount = request.session.get('amount')
        you_save = 0
        coupon = None
        
        # get user and pack details
        userId = request.user.id
        pack = CoinsPack.objects.get(id=packId)
        
        # create an instance of transaction
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user = request.user,
            transaction_id = transaction_id,
            amount = amount,
            status = True
        )
        transaction.save()
       
    #    check if coupon is used for last transaction . Status as True
        if 'coupon_id' in request.session:
            coupon_Id = request.session.get('coupon_id')
            
            # create coupon instance
            couponUse = CouponUsage(
                user = request.user,
                coupon_id =  coupon_Id,
                transaction_id = transaction_id
            )
            couponUse.save()
            
            coupon = Coupon.objects.get(id = coupon_Id)
            
            you_save = float(((Decimal(coupon.discount) / Decimal(100)) * Decimal(pack.price_after_offer)))
            del request.session['coupon_id']
        
        user = User.objects.get(id = userId)
        user.coins += pack.coins
        user.save()          
        
        context = {
            'transaction' : transaction,
            'pack' : pack,
            'user' : request.user,
            'coupon' : coupon,
            'amount' : amount,
            'you_save' : you_save
        }
        
        # delete values in the session after use
        del request.session['pack_id']
        del request.session['in_id']
        del request.session['amount']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            
        return render(request , 'account/payment-completed.html' , context)
    else:
        return redirect('coins')
    

def payment_failed_view(request):
    if request.session.get('pack_id') and request.session.get('in_id'):
        packId = request.session.get('pack_id')
        transaction_id = request.session.get('in_id')
        
        # get user and pack details
        userId = request.user.id
        pack = CoinsPack.objects.get(id=packId)
        amount = request.session.get('amount')
        
        # create transaction instance . Status as False
        transaction = Transaction.objects.create(
            coins_pack_id =  packId,
            user_id = userId,
            transaction_id = transaction_id,
            status = False,
            amount = amount,
        )
        transaction.save()

        context = {
            'pack' : pack
        }
        # delete sessions after use
        del request.session['pack_id']
        del request.session['in_id']
        del request.session['amount']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        
        return render(request , 'account/payment-failed.html' , context)

    else:
        return redirect('coins')
    