from django.contrib import admin
from .models import UploadedImage ,UploadedPDF,ImageRotation,ConvertPdf

# Register your models here.
admin.site.register(UploadedPDF)
admin.site.register(UploadedImage)
admin.site.register(ImageRotation)
admin.site.register(ConvertPdf)