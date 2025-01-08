from django.test import TestCase
# Create your tests here.
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import UploadedImage, UploadedPDF, ImageRotation, ConvertPdf
from django.core.files.uploadedfile import SimpleUploadedFile
import os


@pytest.mark.django_db
class TestUploadImageView:
    def test_upload_image(self):
        client = APIClient()
        url = reverse('upload-image')  # Replace with your URL name for the upload_image view
        with open("D:/MilitaryService/New folder (2)/x.jfif","rb")as img_file:

            image_data = SimpleUploadedFile(img_file.name, img_file.read(), content_type="image/jpeg")
        response = client.post(url, {'file_path': image_data}, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert UploadedImage.objects.count() == 1

@pytest.mark.django_db
class TestUploadPDFView:
    def test_upload_pdf(self):
        client = APIClient()
        url = reverse('upload-pdf')  # Replace with your URL name for the upload_pdf view

        # Open the PDF file in binary mode
        with open("D:/MilitaryService/Desktop/New folder (2)/b.pdf", "rb") as pdf_file:
            pdf_data = SimpleUploadedFile(pdf_file.name, pdf_file.read(), content_type="application/pdf")

        # Make the POST request
        response = client.post(url, {'Location': pdf_data}, format='multipart')

        # Assertions
        assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}"
        assert UploadedPDF.objects.count() == 1, "UploadedPDF object was not created"

@pytest.mark.django_db
class TestRotateImageView:
    def test_rotate_image(self):
        client = APIClient()
        # Create a test image
        #image = ImageRotation.objects.create(image="path/to/test_image.jpg")

        url = reverse('rotate-image')  # Replace with your URL name for the RotateImageView
        with open("D:/MilitaryService/New folder (2)/x.jfif","rb")as img_file:

            image_data = SimpleUploadedFile(img_file.name, img_file.read(), content_type="image/jpeg")
        uploaded_image = UploadedImage.objects.create(file_path=image_data)
        response = client.post(url, {'image': uploaded_image.id, 'angle': 90}, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert ImageRotation.objects.count() == 1

@pytest.mark.django_db
class TestConvertPDFToImageView:
    def test_convert_pdf_to_images(self):
        client = APIClient()
        # Create a test PDF
        
        url = reverse('convert-pdf-to-image')  # Replace with your URL name for the ConvertPDFToImageView
         # Open the PDF file in binary mode
        with open("D:/MilitaryService/Desktop/New folder (2)/b.pdf", "rb") as pdf_file:
            pdf_data = SimpleUploadedFile(pdf_file.name, pdf_file.read(), content_type="application/pdf")
        uploaded_pdf = UploadedPDF.objects.create(Location=pdf_data)
        response = client.post(url, {'pdf_id': uploaded_pdf.id}, format='json')
        assert response.status_code == status.HTTP_200_OK
        # Check if the output folder contains converted images
        assert os.path.exists("output_images/page_1.png")

