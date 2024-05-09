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
from django.contrib import admin
from django.urls import path
from hmsapp.views import home,Userlogin,Clientsignup,forgetpassword,Resetpassword,Userlogout,search
from hmsapp.views import services,serviceproviderhome,bookings,cancelbooking,updatebooking

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('Userlogin/', Userlogin, name='Userlogin'),
    path('Userlogin/forgetpassword/', forgetpassword, name='forgetpassword'),
    path('Clientsignup/', Clientsignup, name='Clientsignup'),
    path('resetpassword/', Resetpassword, name='resetpassword'), 
    path('logout/', Userlogout, name='logout'),
    path('search/', search, name='search'),
    path('services/<str:service_name>/', services, name='services'),
    path('serviceproviderhome/', serviceproviderhome, name='serviceproviderhome'),
    path('bookings/', bookings, name='bookings'),
    path('cancelbooking/', cancelbooking, name='cancelbooking'),
    path('updatebooking/', updatebooking, name='updatebooking'),

]   

