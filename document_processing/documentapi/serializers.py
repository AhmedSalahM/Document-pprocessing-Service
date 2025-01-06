from rest_framework import serializers
from .models import UploadedImage, UploadedPDF ,ImageRotation,ConvertPdf
from PIL import Image
from PyPDF2 import PdfReader

class UploadedImageSerializer(serializers.ModelSerializer):
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ['id', 'file_path', 'uploaded_at', 'width', 'height', 'channels']

    def get_width(self, obj):
        with Image.open(obj.file_path.path) as img:
            return img.width

    def get_height(self, obj):
        with Image.open(obj.file_path.path) as img:
            return img.height

    def get_channels(self, obj):
        with Image.open(obj.file_path.path) as img:
            return len(img.getbands())

class UploadedPDFSerializer(serializers.ModelSerializer):
    num_pages = serializers.SerializerMethodField()
    page_width = serializers.SerializerMethodField()
    page_height = serializers.SerializerMethodField()

    class Meta:
        model = UploadedPDF
        fields = ['id', 'Location', 'uploaded_at', 'num_pages', 'page_width', 'page_height']

    def get_num_pages(self, obj):
        """
        Returns the number of pages in the PDF.
        Handles errors if the PDF is corrupted or incomplete.
        """
        try:
            reader = PdfReader(obj.Location.path)
            return len(reader.pages)
        except Exception as e:  # Generic exception handler
            return None

    def get_page_width(self, obj):
        """
        Returns the width of the first page of the PDF in points.
        Handles errors if the PDF is corrupted or incomplete.
        """
        try:
            reader = PdfReader(obj.Location.path)
            if len(reader.pages) > 0:
                return reader.pages[0].mediabox.width
        except Exception as e:
            return None

    def get_page_height(self, obj):
        """
        Returns the height of the first page of the PDF in points.
        Handles errors if the PDF is corrupted or incomplete.
        """
        try:
            reader = PdfReader(obj.Location.path)
            if len(reader.pages) > 0:
                return reader.pages[0].mediabox.height
        except Exception as e:
            return None

class ImageRotationSerializer(serializers.ModelSerializer):
    image_details = UploadedImageSerializer(source='image', read_only=True)
    rotated_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageRotation
        fields = ['id', 'image', 'image_details', 'angle', 'rotated_image_url', 'rotated_at']

    def get_rotated_image_url(self, obj):
        request = self.context.get('request')
        if obj.rotated_image and request:
            return request.build_absolute_uri(obj.rotated_image.url)
        return None
    

class ConvertPdfSerializer(serializers.ModelSerializer):
    # Nested serializer for UploadedPDF details (read-only)
    #pdf = UploadedPDFSerializer(read_only=True)

    # Allow linking via PDF ID (write-only)
    pdf_id = serializers.PrimaryKeyRelatedField(
        queryset=UploadedPDF.objects.all(),
        source='pdf',  # Maps to the `pdf` field in the model
        write_only=True
    )

    class Meta:
        model = ConvertPdf
        fields = ['id', 'pdf_id']  # Include `convert_pdf` field