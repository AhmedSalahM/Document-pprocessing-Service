## Document processing Service APP
# The project is aimed at helping people to upload images and PDF files to the API and the API will perform some operations on the files and return the results.
# Models
Create a Django project and a REST API using Django Rest Framework (DRF).
The API should have the following endpoints:
○ `POST /api/upload/`: Accepts image and PDF files in base
format and saves them to the server.
○ `GET /api/images/`: Returns a list of all uploaded images.
○ `GET /api/pdfs/`: Returns a list of all uploaded PDFs.
○ `GET /api/images/{id}/`: Returns the details of a specific imag
like the location, width, height, number of channels.
○ `GET /api/pdfs/{id}/`: Returns the details of a specific PDF, li
the location, number of pages, page width, page height.
○ `DELETE /api/images/{id}/`: Deletes a specific imag
○ `DELETE /api/pdfs/{id}/`: Deletes a specific PD
○ `POST /api/rotate/`: Accepts an image ID and rotation angle,
rotates the image, and returns the rotated image.
○ `POST /api/convert-pdf-to-image/`: Accepts a PDF ID, converts
the PDF to an image, and returns the image.
# Dockerize the Django project for easy deployment and testing
# Website Link
https://ahmedsalah2025.pythonanywhere.com/api/images/
# Sample output
https://github.com/AhmedSalahM/Document-processing-Service/blob/main/document_processing/Output_example.png
