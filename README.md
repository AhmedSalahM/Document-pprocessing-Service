# Document processing Service APP
## The project is aimed at helping people to upload images and PDF files to the API and the API will perform some operations on the files and return the results.
## Run Local
1. install python v 3.13.1
2. pip install -r requirment.txt  
3. python manage.py makemigrations
4. python manage.py migrate
5. py manage.py runserver
## Run Using DOCKER
1. docker-compose build
2. docker-compose up
## API.postman_collection
 Provided a postman collection with examples of how to use the API
## Dockerize the Django project for easy deployment and testing
## API Endpoint
https://ahmedsalah2025.pythonanywhere.com/api/images/
## Sample output
![Output_example](https://github.com/user-attachments/assets/8685d501-c31f-4a50-80a2-e1cad8219fd2)
# Some Unit Testing
 def test_upload_image() 

 def test_upload_pdf()

 def test_rotate_image()

 def test_convert_pdf_to_images()

