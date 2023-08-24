from django import forms
from .models import ParsedData

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField()

class ParsedDataForm(forms.ModelForm):
    class Meta:
        model = ParsedData
        exclude = ('customer',)
