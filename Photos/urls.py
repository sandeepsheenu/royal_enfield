from django.urls import path
from . import views

#app_name = 'Photos'

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('correct/', views.correct_data,name='correct_data'),
    path('retrieve/', views.retrieve_customer_data, name='retrieve_customer'),
   
]
