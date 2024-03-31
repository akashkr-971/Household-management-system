from django.shortcuts import redirect, render

# Create your views here.

def home(request):
    return render(request,'home.html')

def login(request):
    return render(request,'login.html')

def signup(request):
    return render(request,'signup.html')

def forgetpassword(request):
    return render(request,'forgetpassword.html')

def Resetpassword(request):
    return render(request,'Resetpassword.html')

def redirect_to_login(request):
    return redirect('login')
