from django.urls import path
from .views import UploadFileView, ListImagesView, ListPDFsView, ImageDetailView, PDFDetailView,upload_image,upload_pdf,RotateImageView,ConvertPDFToImageView

urlpatterns = [
    path('upload/', UploadFileView.as_view(), name='upload-file'),
    path('uploadimage/', upload_image.as_view(), name='upload-image'),
    path('uploadpdf/', upload_pdf.as_view(), name='upload-pdf'),

    path('images/', ListImagesView.as_view(), name='list-images'),
    path('pdfs/', ListPDFsView.as_view(), name='list-pdfs'),
    path('images/<int:pk>/', ImageDetailView.as_view(), name='image-detail'),
    path('pdfs/<int:pk>/', PDFDetailView.as_view(), name='pdf-detail'),
    path('rotate/', RotateImageView.as_view(), name='rotate-image'),
    path('convert-pdf-to-image/', ConvertPDFToImageView.as_view(), name='convert-pdf-to-image'),

]
