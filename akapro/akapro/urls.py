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
from akaapp.views import home
from akaapp.views import login
from akaapp.views import signup
from akaapp.views import forgetpassword
from akaapp.views import Resetpassword
from akaapp.views import redirect_to_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('login/forgetpassword/', forgetpassword, name='forgetpassword'),
    path('signup/', signup, name='signup'),
    path('resetpassword/', Resetpassword, name='resetpassword'), 
]