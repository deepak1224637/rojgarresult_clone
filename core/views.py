from django.shortcuts import render, redirect
from .models import JobPost , AdmitCard, Result, Syllabus,HighlightPost
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
#from.models import AdmitPost

def home(request):
    jobs = JobPost.objects.all().order_by('-posted_on')
    jobs = JobPost.objects.all().order_by('-posted_on')
    cards = AdmitCard.objects.all().order_by('-posted_on')
    results = Result.objects.all().order_by('-posted_on')
    highlights = HighlightPost.objects.all().order_by('-posted_on')
    return render(request, 'home.html',
                  {'jobs':jobs,
                   'cards': cards,
                   'results': results,
                   'highlights': highlights,
                    'now': datetime.now()})

def admit_cards(request):
    cards = AdmitCard.objects.all().order_by('-posted_on')
    return render(request, 'admit_cards.html', {'cards':cards, 'now': datetime.now()})

def results(request):
    results = Result.objects.all().order_by('-posted_on')
    return render(request, 'results.html', {'results': results, 'now': datetime.now()})

def syllabus(request):
    syllabi = Syllabus.objects.all().order_by('-posted_on')
    return render(request, 'syllabus.html', {'syllabi': syllabi, 'now': datetime.now()})

def contact(request):
    return render(request, 'contact.html', {'now': datetime.now()})




def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard_home')
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')

@login_required
def dashboard_home(request):
    return render(request, 'dashboard/dashboard_home.html')


@login_required
def manage_jobs(request):
    return render(request, 'dashboard/manage_jobs.html')
