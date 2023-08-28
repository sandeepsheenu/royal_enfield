from django.contrib import admin

# Register your models here.
from .models import Customer
from .models import ParsedData,UploadedFile

admin.site.register(Customer)
admin.site.register(ParsedData)
admin.site.register(UploadedFile)