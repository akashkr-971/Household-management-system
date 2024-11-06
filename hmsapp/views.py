import base64
from datetime import date
from decimal import Decimal 
from django.db.models import Sum
from django.utils import timezone
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.contrib import messages
from .models import User, Homeowner ,Service , ServiceProvider ,Booking ,Cancellation , Update ,Billing
from .models import Payment ,Reviews ,Sitereview
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Q
import json
import random
import razorpay
# Create your views here.

def landingpage(request):
    return render(request,'index.html')

def home(request):
    user=None;
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
        if user.role=='Service-provider':
            return redirect('serviceproviderhome')
    return render(request,'home.html',{'user': user})

def adminpage(request):
    user = None
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
        if user.role == "admin":
            no_eligibility_providers = ServiceProvider.objects.filter(eligible='No')
            clientusers = User.objects.filter(role='client')
            providers = ServiceProvider.objects.all()
            paymentinfo = Payment.objects.all().order_by('-payment_id')
            bookinginfo = Booking.objects.all().order_by('-booking_id')
            message_list = list(messages.get_messages(request))
            sitereview = Sitereview.objects.all()

            total_employee = ServiceProvider.objects.count()
            total_users = Homeowner.objects.count()
            total_revenue = Payment.objects.filter(payment_status='Success').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            total_bookings = Booking.objects.count()
            Completed_bookings = Booking.objects.filter(status='Paid').count()
            pending_bookings = Booking.objects.filter(status='Pending').count()
            cancelled_bookings = Booking.objects.filter(status='Cancelled').count()

            return render(request, 'adminpage.html', {
                'providers': no_eligibility_providers,
                'user':user,
                'messages':message_list,
                'clientusers' : clientusers,
                'providersdetail' : providers,
                'paymentinfo':paymentinfo,
                'total_employees': total_employee,
                'total_users': total_users,
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'cancelled_bookings': cancelled_bookings,
                'completed_bookings' : Completed_bookings,
                'booking_info':bookinginfo,
                'sitereview' : sitereview,
                })
        
    return render(request,'adminpage.html')

def serviceproviderhome(request):
    user = None
    if 'user_id' in request.session:
        user = User.objects.get(user_id=request.session['user_id'])
        if user.role == "Service-provider":
            provider = ServiceProvider.objects.get(user=user)
            payments = Payment.objects.filter(service_provider_id=provider.service_provider_id)
            total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0

            if provider.has_new_message:
                messages.info(request, provider.new_message)
                provider.has_new_message = False
                provider.new_message = ''
                provider.save()

            if provider.eligible == 'yes' : 
                return render(request, 'serviceproviderhome.html', {'user': user, 'payments': payments ,'total_amount': total_amount})
            elif provider.eligible == 'No':
                messages.warning(request, "Your application is pending approval.")
                return render(request, 'serviceproviderhome.html', {'user': user ,'payments': payments ,'total_amount': total_amount})
            else:
                return render(request, 'serviceproviderhome.html', {'user': user ,'payments': payments ,'total_amount': total_amount})
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
            eligible = 'No'
            service_provider = ServiceProvider.objects.create(user=user, profession=profession, rate=rate , unit=unit , eligible=eligible)
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
            if user.role=='admin' and check_password(password, user.password):
                request.session['user_id'] = user.user_id
                return redirect('adminpage')
            else:
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
        return redirect ('landingpage')
        
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

            user_id = request.session.get('user_id')
            homeowner = Homeowner.objects.get(user_id=user_id)
            available_providers = getavailableproviders(job, date)

            if available_providers:
                service_provider = random.choice(available_providers)
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
                bookingdetails = {
                    'providername' : service_provider.user.full_name,
                    'providernumber' : service_provider.user.phone,
                    'servicedate' : date,
                    'servicerate' : float(rate),
                    'rateunit' : service_provider.unit,
                    'providerrating' : int(service_provider.average_rating),
                    'booked' : 'yes'
                }
                bookingdetails_json = json.dumps(bookingdetails)
                messages.success(request,bookingdetails_json)
                return redirect('home')
            else:
                print('no providers')
                messages.error(request,'No service provider available')
                return redirect('home')
        except Exception as e:
            return HttpResponseBadRequest("Error processing booking: " + str(e))
    else:
        return HttpResponseBadRequest("POST")
    
def getavailableproviders(job,date):
    providers = ServiceProvider.objects.filter(
        profession=job,
        eligible = 'Yes'
        )
    available_providers = providers.exclude(
        Q(bookings__servicedate=date) & Q(bookings__status__in=['Pending', 'Confirmed'])
    )
    return available_providers

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
                    if user.role=='admin':
                        return redirect('adminpage')
        else:
            error_message = "Incorrect OTP try again."
            return render(request, 'verifyotp.html', {'error': error_message})
    return render(request,'verifyotp.html')

def resetpassword(request):
    error_message= None
    action=request.session.get('action')
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
                    if action == 'forgetpassword':
                        hashedpassword = make_password(newpass)
                        user.password=hashedpassword
                        user.save()
                        if user.role=='client':
                            return redirect('home')
                        if user.role=='Service-provider':
                            return redirect('serviceproviderhome')
                    else:
                        print('entered')
                        otp = ''.join(random.choices('0123456789',k=6))
                        action = "resetpassword"
                        print(otp)
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
        billimagefile = request.FILES.get('billimage')
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
            payment_status='Pending',
            bill_image_data = billimagefile,
        )


        billing.save()
        booking.status='Bill created'
        booking.totalrate=totalamount
        booking.save()
        return redirect(serviceproviderhome)
    return render(request, 'serviceproviderhome.html')

def update_bill(request):
    return render(request, 'home.html')

def delete_bill(request):
    if request.method == 'POST':
        bookingid = request.POST.get('deletebillbookingid')
        user_id = request.POST.get('user_id')
        booking = Booking.objects.get(booking_id=bookingid)
        bill = Billing.objects.get(booking=booking)
        bill.delete()
        booking.status = 'Completed'
        booking.save()
        request.session['user_id'] = user_id
        return redirect('home')
    else:
        request.session['user_id'] = user_id
        return render(request, 'home.html')

def getbill(request,booking_id):
    bookings = Booking.objects.get(booking_id = booking_id)
    bill = Billing.objects.get(booking=bookings)

    bill_data = {
        'total_amount': bill.total_amount,
        'items': list(bill.items),
        'bill_image_url': bill.bill_image_data.url if bill.bill_image_data else None,
    }
    print('the bill items are : ',bill_data['items']);
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
            payment_method='Online payment',
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
    print('the booking id is : ',booking_id)
    booking = Booking.objects.get(booking_id=booking_id) 
    print('the booking is ',booking)
    bill = Billing.objects.get(booking=booking)
    print('bill is ',bill)
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
    return JsonResponse({'view': view_data})

def update_account(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        full_name = request.POST['full_name']
        new_user_name = request.POST['user_name']
        email = request.POST['email']
        phone = request.POST['phone']
        location = request.POST['location']
        user = User.objects.get(user_id = user_id)

        if new_user_name != user.user_name and User.objects.filter(user_name=new_user_name).exists():
            messages.error(request, 'User name already exists.')
        else:
            user.full_name = full_name
            user.user_name = new_user_name
            user.email = email
            user.phone = phone
            user.location = location
            user.save()
            messages.success(request, 'Your account has been updated successfully.')
        return render(request, 'accountdetails.html', {'user': user})
    return render(request, 'accountdetails.html', {'user': user})

def delete_account(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        user = User.objects.get(user_id = user_id)
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('landingpage')
    
    return redirect('accountdetails')

def changeeligibility(request):
    if request.method=='POST':
        try:
            provider_id = request.POST.get('providerid')
            eligibility = request.POST.get('eligibility')
            user_id = request.session.get('user_id')
            user = User.objects.get(user_id = user_id)
            provider = ServiceProvider.objects.get(service_provider_id = provider_id)
            if eligibility == 'yes':
                provider.eligible = eligibility
                provider.save()
                admin_message = f"{provider.user.full_name} has been accepted."
                provider_message = "Congratulations! Your application has been accepted." 
            else:
                provider.eligible = 'Not accepted'
                provider.save()
                admin_message = f"Provider {provider.user.full_name} has been rejected."
                provider_message = "We're sorry, but your application has been rejected."
            
            messages.success(request, admin_message)
            provider.has_new_message = True
            provider.new_message = provider_message
            provider.save()
            return redirect('adminpage')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('adminpage')
    return render(request, 'adminpage')

def sitereview(request):
    if request.method == 'POST':
        name = request.POST.get('sitereviewname')
        sitereview = request.POST.get('sitereview')
        rev = Sitereview.objects.create(name=name,review=sitereview)
        rev.save()
        return redirect('home')

 
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


