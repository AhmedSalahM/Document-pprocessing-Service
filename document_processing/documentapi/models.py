from django.db import models
# Create your models here.
class UploadedImage(models.Model):
    file_path = models.ImageField(upload_to='uploads/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image - {self.file_path.name}"

class UploadedPDF(models.Model):
    Location = models.FileField(upload_to='uploads/pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF - {self.Location.name}"
    
class ImageRotation(models.Model):
    image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='rotations')
    angle = models.DecimalField(max_digits=5, decimal_places=2)  # Allow angles like 45.00, 360.00
    rotated_image = models.ImageField(upload_to='uploads/rotated_images/', null=True, blank=True)
    rotated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rotation: {self.angle}° for {self.image.file_path.name}"
class ConvertPdf(models.Model):
    pdf=models.ForeignKey(UploadedPDF,on_delete=models.CASCADE,related_name='convert')

    def __str__(self):
        return f"PDF - {self.pdf}"