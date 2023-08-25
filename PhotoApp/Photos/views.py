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
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from base64 import b64encode
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

api_key = "upload ur api key"
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'






def upload_pdf(request):
    print("post")
    if request.method == 'POST':
        print ("True1")
        form = PDFUploadForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print("True2")
            pdf_file = request.FILES['pdf_file']
            # Save the uploaded file to a temporary directory
            temp_dir = "temp_uploads"
            print("3")
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, pdf_file.name)
            
            with open(file_path, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
            
            parsed_data = process_uploaded_pdf(file_path)
            print(parsed_data)
            print("True6")
            request.session['parsed_data'] = parsed_data
            return redirect('correct_data')
            print("true9")
    else:
        print("True7")
        form = PDFUploadForm()
        print("True8")
        print(form.errors)
    return render(request, 'upload_pdf.html', {'form': form})
#api code starts here

def process_uploaded_pdf(pdf_path):
    extracted_text = extract_fields_from_pdf(pdf_path)
    parsed_data_list  = []

    for text in extracted_text:
        parsed_data = extract_info_from_text(text)
        parsed_data_list .append(parsed_data)

    return parsed_data

def make_image_data_from_image(image):
    img_req = {
        'image': {
            'content': image_to_base64(image)
        },
        'features': [{
            'type': 'DOCUMENT_TEXT_DETECTION',
            'maxResults': 1
        }]
    }
    return json.dumps({"requests": img_req}).encode()

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return b64encode(buffered.getvalue()).decode()

def request_ocr(url, api_key, imgdata):
    response = requests.post(url,
                            data=imgdata,
                            params={'key': api_key},
                            headers={'Content-Type': 'application/json'})
    return response

def gen_cord(result):
    x_coords = [vertex['x'] for vertex in result['boundingPoly']['vertices']]
    y_coords = [vertex['y'] for vertex in result['boundingPoly']['vertices']]
    x_min, y_min = min(x_coords), min(y_coords)
    x_max, y_max = max(x_coords), max(y_coords)
    return result["description"], x_max, x_min, y_max, y_min

def extract_text_from_image(api_key, image, ENDPOINT_URL):
    imgdata = make_image_data_from_image(image)
    response = request_ocr(ENDPOINT_URL, api_key, imgdata)
    if response.status_code == 200 and not response.json().get('error'):
        result = response.json()['responses'][0]['textAnnotations']
        print(result)
        all_text = []  # List to accumulate text
        for annotation in result[1:]:
            text, _, _, _, _ = gen_cord(annotation)
            print(text)
            all_text.append(text)
        return " ".join(all_text)
    else:
        print("Error:", response.content.decode('utf-8'))
        return ""
def convert_page_to_image(pdf_path, page_num):
    images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)
    if images:
        return images[0]
    return None


def extract_fields_from_pdf(pdf_path):
    all_extracted_text = []
    
    # Open the PDF file using PyPDF2
    pdf_reader = PdfReader(pdf_path)
    
    for page_num in range(len(pdf_reader.pages)):
        image = convert_page_to_image(pdf_path, page_num)
        if image is not None:
            extracted_text = extract_text_from_image(api_key, image, ENDPOINT_URL)
            all_extracted_text.append(extracted_text)
            print(all_extracted_text,"this is extracted text")
    return all_extracted_text


def extract_info_from_text(text):
    parsed_data = {
        "booking_id": None,
        "vehicle_model_no": None,
        "model_name": None,
        "name_of_the_customer": None,
        "mobile": None,
        "email_id": None
    }

    booking_id_pattern = r"Booking ID : (\d+)"
    invoice_number_pattern = r"Vehicle Invoice No : (\d+)"
    model_name_pattern = r"Model Name : (.+?) CH No"
    name_pattern = r"NAME OF CUSTOMER (.+?) S / o"
    phone_pattern = r"MOBILE : (\d+)"
    email_pattern = r"EMAIL ID (.+)$"

    booking_id_match = re.search(booking_id_pattern, text)
    if booking_id_match:
        parsed_data["booking_id"] = booking_id_match.group(1)

    invoice_number_match = re.search(invoice_number_pattern, text)
    if invoice_number_match:
        parsed_data["vehicle_model_no"] = invoice_number_match.group(1)

    model_name_match = re.search(model_name_pattern, text)
    if model_name_match:
        parsed_data["model_name"] = model_name_match.group(1).strip()

    name_match = re.search(name_pattern, text)
    if name_match:
        parsed_data["name_of_the_customer"] = name_match.group(1).strip()

    phone_match = re.search(phone_pattern, text)
    if phone_match:
        parsed_data["mobile"] = phone_match.group(1).strip()

    email_match = re.search(email_pattern, text)
    if email_match:
        parsed_data["email_id"] = email_match.group(1).strip()
    print(parsed_data)
    return parsed_data


#api code end here
  
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
        
   

def retrieve_customer_data(request):
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        
        parsed_data_objects = ParsedData.objects.filter(mobile=mobile_number)
        uploaded_files = UploadedFile.objects.filter(parsed_data__in=parsed_data_objects)
        context = {
            'parsed_data_objects': parsed_data_objects,
            'uploaded_files': uploaded_files
        }
        return render(request, 'customer_data.html', context)
    return render(request, 'retrieve_customer.html')

