"""
URL configuration for akapro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from hmsapp.views import home,landingpage,Userlogin,Clientsignup,forgetpassword,resetpassword,Userlogout,search,acceptbooking
from hmsapp.views import services,serviceproviderhome,bookings,cancelbooking,updatebooking,orderhistory,accountdetails
from hmsapp.views import completebooking,finishbooking,verifyotp,clientsignupwithoutotp,jobhistory,publishbill,getbill
from hmsapp.views import initiate_payment,capture_payment,rate_service_provider,fetchreview,update_rate_service_provider,process_withdrawal
from hmsapp.views import viewdetails,update_bill,delete_bill,adminpage,changeeligibility,update_account,delete_account,sitereview,withdrawal_success
from hmsapp.views import contactus,paymentfailed
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',landingpage, name='landingpage'),
    path('home/', home, name='home'),
    path('Userlogin/', Userlogin, name='Userlogin'),
    path('Userlogin/forgetpassword/', forgetpassword, name='forgetpassword'),
    path('Clientsignup/', Clientsignup, name='Clientsignup'),
    path('clientsignupwithoutotp/', clientsignupwithoutotp, name='clientsignupwithoutotp'),
    path('resetpassword/', resetpassword, name='resetpassword'), 
    path('logout/', Userlogout, name='logout'),
    path('search/', search, name='search'),
    path('services/<str:service_name>/', services, name='services'),
    path('serviceproviderhome/', serviceproviderhome, name='serviceproviderhome'),
    path('bookings/', bookings, name='bookings'),
    path('cancelbooking/', cancelbooking, name='cancelbooking'),
    path('updatebooking/', updatebooking, name='updatebooking'),
    path('orderhistory/', orderhistory, name='orderhistory'),
    path('accountdetails/', accountdetails, name='accountdetails'),
    path('acceptbooking/', acceptbooking, name='acceptbooking'),
    path('completebooking/', completebooking, name='completebooking'),
    path('finishbooking/', finishbooking, name='finishbooking'),
    path('verifyotp/', verifyotp, name='verifyotp'),
    path('jobhistory/', jobhistory, name='jobhistory'),
    path('publishbill/', publishbill, name='publishbill'),
    path('update_bill/', update_bill, name='update_bill'),
    path('delete_bill/', delete_bill, name='delete_bill'),
    path('getbill/<int:booking_id>/', getbill, name='getbill'),
    path('initiate_payment', initiate_payment, name='initiate_payment'),
    path('capture_payment/', capture_payment, name='capture_payment'),
    path('rate_service_provider/', rate_service_provider, name='rate_service_provider'),
    path('fetchreview/<int:booking_id>/', fetchreview, name='fetchreview'),
    path('update_rate_service_provider/', update_rate_service_provider, name='update_rate_service_provider'),
    path('viewdetails/<int:booking_id>/', viewdetails, name='viewdetails'),
    path('adminpage/', adminpage, name='adminpage'),
    path('sitereview/', sitereview, name='sitereview'),
    path('changeeligibility/', changeeligibility, name='changeeligibility'),
    path('accountdetails/update/', update_account, name='update_account'),
    path('accountdetails/delete/', delete_account, name='delete_account'),
     path('process_withdrawal', process_withdrawal, name='process_withdrawal'),
    path('withdrawal_success', withdrawal_success, name='withdrawal_success'),
    path('contactus', contactus, name='contactus'),
    path('paymentfailed/', paymentfailed, name='paymentfailed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
