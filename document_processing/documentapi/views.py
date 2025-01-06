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

def getimage( image_id):
    # Get the uploaded image by its ID
    uploaded_image = get_object_or_404(UploadedImage, id=image_id)

    # Open the image using Pillow
    img = Image.open(uploaded_image.image.path)

    # Rotate the image 90 degrees (you can adjust the angle as needed)
    rotated_img = img.rotate(90)

    # Save the rotated image to a BytesIO object to return as a file response
    img_io = BytesIO()
    rotated_img.save(img_io, 'JPEG')
    img_io.seek(0)

    # Prepare the file for response
    image_file = InMemoryUploadedFile(
        img_io, None, 'rotated_image.jpg', 'image/jpeg', img_io.getbuffer().nbytes, None
    )

    # You can save this new rotated image as a new model or directly return it
    # For this example, we return the image as a downloadable response
    response = JsonResponse({"message": "Image rotated successfully"})
    response['X-Rotated-Image'] = image_file

    return response
class UploadFileView(generics.CreateAPIView):
    """
    Handles uploading of both images and PDFs.
    """
    def get_queryset(self):
        file_type = self.request.data.get("file_type")
        if file_type == "image":
            return UploadedImage.objects.all()
        elif file_type == "pdf":
            return UploadedPDF.objects.all()
        else:
            raise ValidationError({"file_type": "Invalid file type. Accepted types are 'image' and 'pdf'."})

    def get_serializer_class(self):
        file_type = self.request.data.get("file_type")
        if file_type == "image":
            return UploadedImageSerializer
        elif file_type == "pdf":
            return UploadedPDFSerializer
        else:
            raise ValidationError({"file_type": "Invalid file type. Accepted types are 'image' and 'pdf'."})

    
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
'''
class ConvertPDFToImageView(generics.ListCreateAPIView):
    """
    Handles listing and creating ConvertPdf instances.
    """
    queryset = ConvertPdf.objects.all()
    serializer_class = ConvertPdfSerializer

    def create(self, request, *args, **kwargs):
        pdf_id = self.request.data.get('pdf_id')
        if not pdf_id:
            return Response(
                {"error": "PDF ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the PDF object
            pdf = UploadedPDF.objects.get(id=pdf_id)
            pdf_path = pdf.Location.path

            images = convert_from_path(pdf_path)
            created_instances = []

            for i, image in enumerate(images):
                image_filename = f"pdf_page_{pdf_id}_{i + 1}.jpg"
                image_path = os.path.join(settings.MEDIA_ROOT, "uploads/convert_pdf", image_filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path, "JPEG")

                # Create a ConvertPdf instance for each image
                convert_pdf_instance = ConvertPdf.objects.create(pdf=pdf, convert_pdf=image_filename)
                created_instances.append(convert_pdf_instance)

            # Serialize and return the created instances
            serializer = self.get_serializer(created_instances, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UploadedPDF.DoesNotExist:
            return Response(
                {"error": "PDF not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
     class ConvertPDFToImageView(generics.ListCreateAPIView):
    """
    Handles listing and creating ConvertPdf instances.
    """
    queryset = ConvertPdf.objects.all()
    serializer_class = ConvertPdfSerializer

    def create(self, request, *args, **kwargs):
        pdf_id =self.request.data.get('pdf_id')
        if not pdf_id:
            return Response(
                {"error": "PDF ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the image object
            pdf = UploadedPDF.objects.get(id=pdf_id)
            pdf_path = pdf.Location.path
            images = convert_from_path(pdf_path)
            created_instances = []
            
            for i, image in enumerate(images):

                image_path =os.path.join(settings.MEDIA_ROOT, "uploads/convert_pdf/pdf_page_{pdf_id}_{i + 1}.jpg")
                image.save(image_path, "JPEG")
                
                # Create a ConvertPdf instance for each image
                convert_pdf_instance = ConvertPdf.objects.create(pdf=pdf, convert_pdf=image_path)
                created_instances.append(convert_pdf_instance)

            # Serialize and return the created instances
            serializer = self.get_serializer(created_instances, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UploadedPDF.DoesNotExist:
            return Response(
                {"error": "PDF not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

'''

'''
class UploadFileView(APIView):
    def post(self, request):
        file_type = request.data.get('file_type')
        file = request.FILES.get('file')

        if file_type == 'image':
            uploaded_image = UploadedImage.objects.create(file_path=file)
            serializer = UploadedImageSerializer(uploaded_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif file_type == 'pdf':
            uploaded_pdf = UploadedPDF.objects.create(file_path=file)
            serializer = UploadedPDFSerializer(uploaded_pdf)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)
'''

