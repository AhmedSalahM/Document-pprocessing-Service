# Generated by Django 5.1.4 on 2025-01-04 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentapi', '0004_imagerotation_rotated_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvertPdf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('convert_pdf', models.ImageField(blank=True, null=True, upload_to='uploads/convert_pdf/')),
                ('pdf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='convert', to='documentapi.uploadedpdf')),
            ],
        ),
    ]