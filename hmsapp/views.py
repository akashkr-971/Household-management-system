from datetime import date 
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.contrib import messages
from .models import User, Homeowner ,Service , ServiceProvider ,Booking ,Cancellation , Update ,Billing
from .models import Payment ,Reviews
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import random
import razorpay
# Create your views here.

def home(request):
    user=None;
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
        if user.role=='Service-provider':
            return redirect('serviceproviderhome')
    return render(request,'home.html',{'user': user})

def serviceproviderhome(request):
    user = None
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
        if user.role == "Service-provider":
            return render(request, 'serviceproviderhome.html', {'user': user})
    return render(request, 'Userlogin.html')

def clientsignupwithoutotp(request):
    if request.method == 'POST':
        full_name = request.POST.get('fname')
        username = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        location = request.POST.get('location')
        role = request.POST.get('role')
        phone = request.POST.get('phone')

        if User.objects.filter(user_name=username).exists() or User.objects.filter(email=email).exists():
            return render(request, 'Clientsignup.html', {'error': 'Username or email already exists'})
        hashed_password = make_password(password)

        user = User.objects.create(full_name=full_name, user_name=username, email=email, phone=phone, role=role, password=hashed_password, location=location)
        request.session['user_id'] = user.user_id
        if role=='client':
            homeowner = Homeowner.objects.create(user=user)
            return redirect('home')
        if role=='Service-provider':
            profession = request.POST.get('Profession')
            rate = request.POST.get('rate')
            unit = request.POST.get('unit')
            service_provider = ServiceProvider.objects.create(user=user, profession=profession, rate=rate , unit=unit)
            return redirect('serviceproviderhome')
    
    return render(request, 'Clientsignup.html')

def Clientsignup(request):
        if request.method == 'POST':
            full_name = request.POST.get('fname')
            username = request.POST.get('uname')
            email = request.POST.get('email')
            password = request.POST.get('pass')
            location = request.POST.get('location')
            role = request.POST.get('role')
            phone = request.POST.get('phone')

            if User.objects.filter(user_name=username).exists() or User.objects.filter(email=email).exists():
                return render(request, 'Clientsignup.html', {'error': 'Username or email already exists'})

            request.session['signup_data'] = {
                'full_name': full_name,
                'username': username,
                'email': email,
                'password': password,
                'location': location,
                'role': role,
                'phone': phone
            }
            
            otp = ''.join(random.choices('0123456789',k=6))
            action = "signup"
            send_mail(
                'Sign-up OTP',
                f'Your OTP for sign-up is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            request.session['resetotp'] = otp
            request.session['action'] = action
            request.session['reset_email'] = email
            return redirect(verifyotp)
        return render(request, 'Clientsignup.html')

def Userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        try:
            user = User.objects.get(user_name=username)
            print(user.password)
            print(check_password(password,user.password))
            if check_password(password, user.password) and user.role=='client':
                request.session['user_id'] = user.user_id
                return redirect('home')
            elif check_password(password, user.password) and user.role=='Service-provider':
                request.session['user_id'] = user.user_id
                return redirect('serviceproviderhome')
            else:
                print('authetication failed')
        except User.DoesNotExist:
            pass
        error_message = "Invalid username or password."
        return render(request, 'Userlogin.html', {'error': error_message})

    return render(request, 'Userlogin.html')

def Userlogout(request):
        logout(request)
        return redirect ('home')
        
def search(request):
    query = request.get('search')

def services(request,service_name):
    service_providers = ServiceProvider.objects.filter(profession=service_name)
    service = Service.objects.get(service_name=service_name)
    return render(request, 'services.html', {'service_providers': service_providers, 'service_name': service_name})

def bookings(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            job = request.POST.get('job')
            jobdesc = request.POST.get('jobdesc')
            date = request.POST.get('date')
            time = request.POST.get('time')
            location = request.POST.get('location')
            landmark = request.POST.get('LandMark')
            service_provider_id = request.POST.get('provider_id')

            if service_provider_id:
                service_provider_id = int(service_provider_id)
                print('Service Provider ID:', service_provider_id)  # Debugging statement
                user_id = request.session.get('user_id')
                service_provider = ServiceProvider.objects.get(service_provider_id=service_provider_id)
                homeowner = Homeowner.objects.get(user_id=user_id)  # Get the Homeowner instance
                rate = service_provider.rate 

                booking = Booking.objects.create(
                    homeowner=homeowner, 
                    service_provider=service_provider,
                    name=username,
                    job=job,
                    jobdescription=jobdesc,
                    rate=rate,
                    servicedate=date,
                    servicetime=time,
                    location=location,
                    landmark=landmark,
                    status='Pending'
                )
                messages.success(request, 'Booking successful!')
                return redirect('home')
            else:
                return HttpResponseBadRequest("Service Provider ID is missing")
        except Exception as e:
            return HttpResponseBadRequest("Error processing booking: " + str(e))
    else:
        return HttpResponseBadRequest("POST")

def cancelbooking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        cancellation_reason = request.POST.get('cancellation_reason')
        homeownerid= request.POST.get('homeownerid')
        serviceproviderid= request.POST.get('serviceproviderid')

        booking = get_object_or_404(Booking, pk=booking_id)
        homeowner = get_object_or_404(Homeowner, pk=homeownerid)
        service_provider = get_object_or_404(ServiceProvider, pk=serviceproviderid)
        booking = Booking.objects.get(pk=booking_id)
        
        cancellation = Cancellation.objects.create(
            booking=booking,
            homeowner=homeowner,  
            service_provider=service_provider,
            reason=cancellation_reason
        )
        booking.status = 'Cancelled'
        booking.save()
        
        return redirect('home')
    else:
        return render(request, 'home')

def updatebooking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        homeowner_id = request.POST.get('homeowner_id')
        service_provider_id = request.POST.get('service_provider_id')
        update_description = request.POST.get('update_description')
        updatetodate = request.POST.get('updatetodate')
        updatetotime = request.POST.get('updatetotime')

        booking = Booking.objects.get(pk=booking_id)
        homeowner = Homeowner.objects.get(pk=homeowner_id)
        service_provider = ServiceProvider.objects.get(pk=service_provider_id)

        booking.servicedate = updatetodate
        booking.servicetime = updatetotime
        booking.isupdated='yes'
        booking.status='Pending'
        booking.save()

        update = Update.objects.create(
            booking=booking,
            homeowner=homeowner,
            service_provider=service_provider,
            updateto_date = updatetodate,
            description=update_description,
            updateto_time = updatetotime
        )
        return redirect('home')
    else:
        return redirect('home')

def forgetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = ''.join(random.choices('0123456789',k=6))
        action = "forgetpassword"
        try:
            user = User.objects.get(email=email)
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            request.session['resetotp'] = otp
            request.session['action'] = action
            request.session['reset_email'] = email
            return redirect(verifyotp)
        except User.DoesNotExist:
            error_message = 'User does not exists'
            return render(request, 'Userlogin.html', {'error': error_message})
    return render(request,'forgetpassword.html')

def verifyotp(request):
    if request.method == 'POST':
        email=request.session.get('reset_email')
        sendotp = request.session.get('resetotp')
        enteredotp = request.POST.get('enteredotp')
        action=request.session.get('action')
        if sendotp == enteredotp:
            if action == 'forgetpassword':
                user = User.objects.get(email=email)
                request.session['user_id'] = user.user_id
                return redirect('resetpassword')
            if action == 'signup':
                signup_data = request.session.get('signup_data')
                if signup_data:
                    full_name = signup_data.get('full_name')
                    username = signup_data.get('username')
                    email = signup_data.get('email')
                    password = signup_data.get('password')
                    location = signup_data.get('location')
                    role = signup_data.get('role')
                    phone = signup_data.get('phone')

                    hashed_password = make_password(password)

                    user = User.objects.create(full_name=full_name, user_name=username, email=email, phone=phone, role=role, password=hashed_password, location=location)
                    request.session['user_id'] = user.user_id
                    if role=='client':
                        homeowner = Homeowner.objects.create(user=user)
                        return redirect('home')
                    if role=='Service-provider':
                        profession = request.POST.get('Profession')
                        rate = request.POST.get('rate')
                        unit = request.POST.get('unit')
                        service_provider = ServiceProvider.objects.create(user=user, profession=profession, rate=rate , unit=unit)
                        return redirect('serviceproviderhome')
            if action == 'resetpassword':
                resetpass = request.session.get('resetpass_data')
                if resetpass :
                    user_id = resetpass.get('user_id')
                    newpass = resetpass.get('newpass')
                    hashedpassword=make_password(newpass)
                    user = User.objects.get(user_id=user_id)
                    user.password=hashedpassword
                    user.save()
                    if user.role=='client':
                        return redirect('home')
                    if user.role=='Service-provider':
                        return redirect('serviceproviderhome')
        else:
            error_message = "Incorrect OTP try again."
            return render(request, 'verifyotp.html', {'error': error_message})
    return render(request,'verifyotp.html')

def Resetpassword(request):
    error_message= None
    if 'user_id' in request.session:
        if request.method == 'POST':
            user_id = request.session['user_id']
            newpass = request.POST.get('npass')
            cnfpass = request.POST.get('cnfpass')
            try:
                user=User.objects.get(user_id=user_id)
                email = user.email
                if newpass==cnfpass:
                    request.session['resetpass_data'] = {
                        'user_id' : user_id,
                        'newpass' : newpass
                    }
                    otp = ''.join(random.choices('0123456789',k=6))
                    action = "resetpassword"
                    send_mail(
                        'Reset password OTP',
                        f'Your OTP for Resetting password is: {otp}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    request.session['resetotp'] = otp
                    request.session['action'] = action
                    request.session['reset_email'] = email
                    return redirect(verifyotp)
                else:
                    error_message='Password does not match'
            except:
                error_message= 'User does not exists'
        return render(request,'Resetpassword.html',{'error': error_message})
    else:
        return render(request,'Userlogin.html')

def orderhistory(request):
    user=None;
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
    return render(request,'orderhistory.html',{'user': user})

def jobhistory(request):
    user=None;
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
    return render(request,'jobhistory.html',{'user': user})

def accountdetails(request):
    user=None;
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
    return render(request,'accountdetails.html',{'user': user})

def acceptbooking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')

        booking=Booking.objects.get(booking_id=booking_id)
        booking.status = new_status
        booking.save()
    return redirect('serviceproviderhome')

def completebooking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')

        booking=Booking.objects.get(booking_id=booking_id)
        booking.status = new_status
        booking.save()
    return redirect('serviceproviderhome')

def finishbooking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')

        booking=Booking.objects.get(booking_id=booking_id)
        booking.status = new_status 
        booking.save()
        homeowner = booking.homeowner
        service_provider=booking.service_provider
        amount = booking.totalrate
        payment = Payment.objects.create(
            order_id = 'none',
            booking = booking,
            homeowner = homeowner,
            service_provider=service_provider,
            amount=amount,
            payment_status='Paid',
            razorpay_payment_id = 'none',
            payment_method = 'cash on hand'
        )
    return redirect('serviceproviderhome')

def publishbill(request):
    if request.method == 'POST':
        billdatajson = request.POST.get('billData')
        totalamount = request.POST.get('totalfinalamount')
        bookingid = request.POST.get('bookingid')
    
        booking = Booking.objects.get(booking_id=bookingid)
        homeowner = booking.homeowner
        service_provider = booking.service_provider

        try:
            if billdatajson:
                billdata = json.loads(billdatajson)
                print('The data in the bill data is : ',billdatajson)
            else:
                print('data is not found')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)


        billing = Billing(
            booking=booking,
            homeowner=homeowner,
            service_provider=service_provider,
            items=billdata,
            total_amount=totalamount,
            date=date.today(),
            payment_status='Pending'
        )
        billing.save()
        booking.status='Bill created'
        booking.totalrate=totalamount
        booking.save()
        return redirect(serviceproviderhome)
    return render(request, 'serviceproviderhome.html')

def getbill(request,booking_id):
    bookings = Booking.objects.get(booking_id = booking_id)
    bill = Billing.objects.get(booking=bookings)
    bill_data = {
        'total_amount': bill.total_amount,
        'items': list(bill.items)
    }
    return JsonResponse({'bill': bill_data})

def initiate_payment(request):
    if request.method == 'POST':
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET))
        amount = request.POST.get('totalamountinput')
        amount = float(amount) * 100
        amount = int(amount)
        userid = request.POST.get('userid')
        bookingid = request.POST.get('billbookingid')

        user = User.objects.get(user_id = userid)
        booking = Booking.objects.get(booking_id = bookingid)
        homeowner  = booking.homeowner
        service_provider  = booking.service_provider

        order = client.order.create(dict(amount=amount, currency="INR", payment_capture='0'))
        payment = Payment(
            order_id=order['id'],
            booking=booking,
            homeowner=homeowner,
            service_provider=service_provider,
            amount=amount/100,  
            method='Online payment',
            payment_status='Pending'
        )
        payment.save()
        
        context = {
            'razorpay_key': settings.RAZOR_PAY_KEY_ID,
            'amount': amount,
            'business_name': 'Household management system',
            'order_id': order['id'],
            'callback_url': 'http://127.0.0.1:8000/capture_payment/',
            'user': user,
        }
        return render(request, 'payment_page.html',context)

    return render(request, 'home.html')

def rate_service_provider(request):
    if request.method =='POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')
        bookingid = request.POST.get('bookingid')
        booking = Booking.objects.get(booking_id=bookingid)
        provider = booking.service_provider
        review = Reviews(
            service_provider=provider,
            booking=booking,
            rating=stars,
            review=comment,
        )
        review.save()
        booking.israted='Yes'
        booking.save()
        average_rating = provider.calculate_average_rating()
        provider.average_rating = average_rating
        provider.save()
        userid = booking.homeowner.user.user_id
        print('the userid is ',userid)
        request.session['user_id'] = userid
        return redirect(reverse('orderhistory'))

def fetchreview(request,booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    review = Reviews.objects.get(booking=booking)
    reviews_data = {
        'rating':review.rating,
        'comment':review.review
    }
    print(reviews_data)
    return JsonResponse({'review': reviews_data})
    
def update_rate_service_provider(request):
    if request.method =='POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')
        bookingid = request.POST.get('bookingid')
        booking = Booking.objects.get(booking_id=bookingid)
        provider = booking.service_provider

        review = Reviews.objects.get(booking=booking)
        review.rating = stars
        review.review = comment
        review.review_date = timezone.now()
        review.save()
        average_rating = provider.calculate_average_rating()
        provider.average_rating = average_rating
        provider.save()
        userid = booking.homeowner.user.user_id
        request.session['user_id'] = userid
        return redirect(reverse('orderhistory'))

def viewdetails(request,booking_id):
    booking = Booking.objects.get(booking_id=booking_id) 
    bill = Billing.objects.get(booking=booking)
    payment = Payment.objects.get(booking=booking)
    view_data = {
        'bill_id' : bill.bill_id,
        'pdate' : payment.date,
        'pid' : payment.payment_id, 
        'ptid' : payment.razorpay_payment_id, 
        'prmethod' : payment.payment_method,
        'pstatus' : payment.payment_status,
        'bcomplete' : bill.date
    }
    print(view_data)
    return JsonResponse({'view': view_data})

    
@csrf_exempt
def capture_payment(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET))
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = client.utility.verify_payment_signature(params_dict)
            if result is not None:
                transaction = client.payment.fetch(payment_id)
                payment_method = transaction.get('method')
                payment = Payment.objects.get(order_id=order_id)
                payment.payment_status = 'Success'
                payment.razorpay_payment_id = payment_id
                payment.payment_method = payment_method
                payment.save()

                booking = payment.booking
                booking.status = 'Paid'
                booking.totalrate = payment.amount
                booking.save()

                user_id = payment.homeowner.user.user_id
                authorized_amount = payment.amount
                amount_in_paise = int(authorized_amount * 100)
                captured_payment = client.payment.capture(payment_id, amount_in_paise)
                return render(request, 'payment_status.html', {'status': 'success','razorpay_payment_id': payment_id,'user_id': user_id})
            else:
                return render(request, 'payment_status.html', {'status': 'failed','user_id': user_id})
        except (razorpay.errors.SignatureVerificationError, ValueError, KeyError) as e:
            print('Error:', e)
            return render(request, 'home.html', {'status': 'failed'})
    return HttpResponseBadRequest()

    