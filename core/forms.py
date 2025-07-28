from django import forms
from .models import JobPost
from .models import AdmitCard

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'apply_link', 'last_date']
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }




class AdmitCardForm(forms.ModelForm):
    class Meta:
        model = AdmitCard
        fields = ['title', 'exam_date' 'download_link', 'date_published']
        widgets = {
            'date_published': forms.DateInput(attrs={'type': 'date'})
            #'exam_date': forms.DateInput(attrs={'type': 'date'}), # type: ignore
        }

