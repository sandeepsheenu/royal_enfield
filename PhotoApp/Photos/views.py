import requests
import re
import PyPDF2
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, ParsedData,UploadedFile
from .forms import PDFUploadForm, ParsedDataForm
import pdfplumber
from io import BytesIO
from django.urls import reverse
import json
import os
import re
from django.forms import formset_factory






def upload_pdf(request):
    print("post")
    if request.method == 'POST':
        print ("True1")
        form = PDFUploadForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print("True2")
            pdf_file = request.FILES['pdf_file']
            
            parsed_data = parse_pdf(pdf_file)  # Call your parsing function here
            print(parsed_data)
            print("True6")
            request.session['parsed_data'] = parsed_data
            return redirect('correct_data')

            #form_with_initial_data = ParsedDataForm(initial=parsed_data)
            #print(form_with_initial_data)
            #return (request,'correct_data.html')
            #return render(request,'correct_data.html', {'form': form_with_initial_data})
            #return render(request, 'correct_data.html', {'parsed_data': parsed_data})
            print("true9")
    else:
        print("True7")
        form = PDFUploadForm()
        print("True8")
        print(form.errors)
    return render(request, 'upload_pdf.html', {'form': form})

def parse_pdf(pdf_file):
    parsed_data = {}
    
    try:
        # with open(pdf_file, 'rb') as pdf_file:
        #     pdf_reader = PyPDF2.PdfReader(pdf_file)
        #     page_text = ' '.join([page.extract_text() for page in pdf_reader.pages])
          with BytesIO(pdf_file.read()) as pdf_stream:
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            page_text = ' '.join([page.extract_text() for page in pdf_reader.pages])

            booking_id = re.search(r'Booking id:\s*(\d+)', page_text)
            if booking_id:
                parsed_data['booking_id'] = int(booking_id.group(1))
            
            vehicle_model_no = re.search(r'Vehicle model no:\s*(\d+)', page_text)
            if vehicle_model_no:
                parsed_data['vehicle_model_no'] = int(vehicle_model_no.group(1))
            
            model_name = re.search(r'Model name:\s*([^\n]+)', page_text)
            if model_name:
                parsed_data['model_name'] = model_name.group(1).strip()
            
            customer_name = re.search(r'Name of the customer:\s*([^\n]+)', page_text)
            if customer_name:
                parsed_data['name_of_the_customer'] = customer_name.group(1).strip()
            
            mobile = re.search(r'Mobile:\s*([\d\s-]+)', page_text)
            if mobile:
                parsed_data['mobile'] = mobile.group(1).strip()
            
            email_id = re.search(r'Email id:\s*([^\n]+)', page_text)
            if email_id:
                parsed_data['email_id'] = email_id.group(1).strip()

    except Exception as e:
        print(f"Error: {e}")
    #print(parsed_data)
    return parsed_data
  
def correct_data(request):
    parsed_data = request.session.get('parsed_data')
    print(parsed_data,2)
    if not parsed_data:
        return redirect('upload_pdf')
    if request.method == 'POST':
        parsed_data_form = ParsedDataForm(request.POST)
        if parsed_data_form.is_valid():
            corrected_data = parsed_data_form.cleaned_data
            uploaded_files = request.FILES.getlist('uploaded_files')

            #parsed_data_obj = ParsedData(**parsed_data, **corrected_data)
            merged_data = {**parsed_data, **corrected_data}

            parsed_data_obj = ParsedData(**merged_data)
            parsed_data_obj.save()

            for uploaded_file in uploaded_files:
                UploadedFile.objects.create(parsed_data=parsed_data_obj, file=uploaded_file)

            del request.session['parsed_data']  # Clear session data
            return render(request, 'thankyou.html')
   
    else:
         parsed_data_form = ParsedDataForm(initial=parsed_data)

    return render(request, 'correct_data.html', {'parsed_data_form': parsed_data_form})
        
    #return render(request, 'correct_data.html', {'parsed_data_form': parsed_data_form, 'file_formset': file_formset})
# def correct_data(request):
#     print("true10")
#     if request.method == 'POST':
#         print(True)
#         form = ParsedDataForm(request.POST)

#         print(form)
#         if form.is_valid():
#             # Save corrected data
#             parsed_data = form.save(commit=False)
#             print(parsed_data)
#             parsed_data.customer = Customer.objects.create()
#             parsed_data.save()
#             #return redirect('upload_pdf')
           
#             return render(request,'thankyou.html')
#     else:
#         print("true11")
#         form = ParsedDataForm()
#     return render(request, 'correct_data.html', {'form': form})

# def thankyou(request) :
#     return render(request,'thankyou.html')
def retrieve_customer_data(request):
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        #1parsed_data_obj = get_object_or_404(ParsedData, mobile=mobile_number)
        #1uploaded_files = UploadedFile.objects.filter(parsed_data=parsed_data_obj)
        parsed_data_objects = ParsedData.objects.filter(mobile=mobile_number)
        uploaded_files = UploadedFile.objects.filter(parsed_data__in=parsed_data_objects)
        context = {
            'parsed_data_objects': parsed_data_objects,
            'uploaded_files': uploaded_files
        }
        return render(request, 'customer_data.html', context)
    return render(request, 'retrieve_customer.html')
# def retrieve_customer_data(request):
#     if request.method == 'POST':
#         mobile_number = request.POST.get('mobile_number')
#         #customer = get_object_or_404(Customer, mobile_number=mobile_number)
#        # parsed_data = ParsedData.objects.filter(customer=customer)
#         #parsed_data = ParsedData.objects.filter(mobile=mobile_number)
#         #print(parsed_data)
#         return render(request, 'customer_data.html', {'parsed_data': parsed_data})
#     return render(request, 'retrieve_customer.html')
