from django.db import models

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    mobile_number = models.CharField(max_length=20)

class ParsedData(models.Model):
    booking_id = models.CharField(max_length=255)
    vehicle_model_no = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    name_of_the_customer = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email_id = models.EmailField()
    # Other fields for parsed data
    # def __str__(self):
    #     return f'Booking ID: {self.booking_id}, Customer: {self.name_of_the_customer}'
class UploadedFile(models.Model):
    parsed_data = models.ForeignKey(ParsedData, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')