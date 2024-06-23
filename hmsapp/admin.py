from django.contrib import admin
from .models import *  

for model in [model for model in dir() if model.istitle()]:
    try:
        admin.site.register(eval(model))
    except:
        pass

