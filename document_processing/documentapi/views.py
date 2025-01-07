from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadedImage, UploadedPDF ,ImageRotation,ConvertPdf
from .serializers import UploadedImageSerializer, UploadedPDFSerializer,ImageRotationSerializer,ConvertPdfSerializer
from django.conf import settings
from rest_framework import generics ,serializers
from rest_framework.exceptions import ValidationError
from PIL import Image
from pdf2image import convert_from_path
from rest_framework.decorators import api_view
from io import BytesIO
from django.http import HttpResponse
import fitz  # PyMuPDF
import os

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import UploadedImage
    
class upload_image(generics.CreateAPIView):
    queryset=UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

class upload_pdf(generics.CreateAPIView):
    queryset=UploadedPDF.objects.all()
    serializer_class = UploadedPDFSerializer
class ListImagesView(ListAPIView):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

class ListPDFsView(ListAPIView):
    queryset = UploadedPDF.objects.all()
    serializer_class = UploadedPDFSerializer

class ImageDetailView(generics.RetrieveDestroyAPIView):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

class PDFDetailView(generics.RetrieveDestroyAPIView):
    queryset = UploadedPDF.objects.all()
    serializer_class = UploadedPDFSerializer


class RotateImageView(generics.ListCreateAPIView):
    queryset = ImageRotation.objects.all()
    serializer_class = ImageRotationSerializer

    def perform_create(self, serializer):
        image_id = self.request.data.get('image')
        angle = self.request.data.get('angle')

        if not image_id or not angle:
            raise ValidationError({"error": "Both 'image' and 'angle' are required."})

        try:
            # Fetch the image object
            image_obj = UploadedImage.objects.get(id=image_id)
            image_path = image_obj.file_path.path

            # Rotate the image
            with Image.open(image_path) as img:
                rotated_img = img.rotate(float(angle), expand=True)
                rotated_image_name = f"rotated_{os.path.basename(image_path)}"
                rotated_image_path = os.path.join(settings.MEDIA_ROOT, 'uploads/rotated_images', rotated_image_name)

                os.makedirs(os.path.dirname(rotated_image_path), exist_ok=True)
                rotated_img.save(rotated_image_path)

                # Save rotation record
                serializer.save(
                    image=image_obj,
                    angle=angle,
                    rotated_image=f'uploads/rotated_images/{rotated_image_name}'
                )
                #return HttpResponse(rotated_image_path, content_type='image/png')

            
        except UploadedImage.DoesNotExist:
            raise ValidationError({"error": "Image with the given ID does not exist."})
        except Exception as e:
            raise ValidationError({"error": f"An unexpected error occurred: {str(e)}"})

def pdf_to_images(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate through each page
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)
        
        # Render the page to a pixmap (image)
        pix = page.get_pixmap()
        
        # Define the output image path
        output_image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        
        # Save the image
        pix.save(output_image_path)
        
    
    print(f"PDF has been converted to images and saved in {output_folder}")
class ConvertPDFToImageView(generics.ListCreateAPIView):
    queryset = ConvertPdf.objects.all()
    serializer_class = ConvertPdfSerializer

    def perform_create(self, serializer):
        # Create the ConvertPdf instance
        convert_pdf = serializer.save()

        # Retrieve the linked PDF file
        uploaded_pdf = convert_pdf.pdf
        pdf_path = uploaded_pdf.Location.path

        # Check if the PDF exists
        if not os.path.exists(pdf_path):
            raise Exception(f"PDF file {pdf_path} not found.")

        try:
            # Convert the PDF to images (one image per page)
            output_folder = "output_images"
            pdf_to_images(pdf_path, output_folder)
            # Return the image as a response
            return HttpResponse(output_folder+'/page_1.png')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        # Use the serializer to validate and create the conversion record
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Perform the conversion and return the image
            return self.perform_create(serializer)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


