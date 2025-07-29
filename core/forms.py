from django import forms
from .models import JobPost
from .models import AdmitCard 
from .models import Result
from .models import HighlightPost
from .models import Subscriber

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'category', 'description', 'last_date',
            'how_to_apply', 'important_links', 'important_dates',
            'eligibility', 'age_limit', 'exam_fee', 'total_posts',
            'apply_link']
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }




class AdmitCardForm(forms.ModelForm):
    class Meta:
        model = AdmitCard
        fields = ['title', 'exam_date' , 'download_link', 'date_published']
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date'}),
            'date_published': forms.DateInput(attrs={'type': 'date'}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['title', 'result_date', 'result_link']
        widgets ={
            'exam_date': forms.DateInput(attrs={'type': 'data'})
        }

class HighlightPostForm(forms.ModelForm):
    class Meta:
        model = HighlightPost
        fields = ['title','link', 'post_count', 'bg_color']


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        