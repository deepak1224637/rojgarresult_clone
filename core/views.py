from django.shortcuts import render, redirect , get_object_or_404
from .models import JobPost , AdmitCard, Result, Syllabus,HighlightPost
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import JobPostForm, ResultForm , HighlightPostForm

from .models import AdmitCard
from .forms import AdmitCardForm


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


# @login_required
# def manage_jobs(request):
#     jobs = JobPost.objects.all().order_by('-posted_on')  # Latest first
#     return render(request, 'dashboard/manage_jobs.html', {'jobs': jobs})

@login_required
def manage_jobs(request):
    jobs = JobPost.objects.all().order_by('-posted_on')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_jobs')
    else:
        form = JobPostForm()

    return render(request, 'dashboard/manage_jobs.html', {
        'jobs': jobs,
        'form': form
    })



# EDIT
@login_required
def edit_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('manage_jobs')
    else:
        form = JobPostForm(instance=job)
    return render(request, 'dashboard/edit_job.html', {'form': form, 'job': job})

# DELETE
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    job.delete()
    return redirect('manage_jobs')






@login_required
def manage_admit_cards(request):
    cards = AdmitCard.objects.all().order_by('-posted_on')

    if request.method == 'POST':
        form = AdmitCardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_admit_cards')
    else:
        form = AdmitCardForm()

    return render(request, 'dashboard/manage_admit_cards.html', {
        'form': form,
        'cards': cards
    })

@login_required
def edit_admit_card(request, card_id):
    card = get_object_or_404(AdmitCard, id=card_id)
    form = AdmitCardForm(request.POST or None, instance=card)
    if form.is_valid():
        form.save()
        return redirect('manage_admit_cards')
    return render(request, 'dashboard/edit_admit_card.html', {'form': form, 'card': card})

@login_required
def delete_admit_card(request, card_id):
    card = get_object_or_404(AdmitCard, id=card_id)
    card.delete()
    return redirect('manage_admit_cards')

@login_required
def manage_results(request):
    results = Result.objects.all().order_by('-posted_on')
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_results')
    else:
        form = ResultForm()
    return render(request, 'dashboard/manage_results.html', {'form': form, 'results': results})

@login_required
def edit_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    form = ResultForm(request.POST or None, instance=result)
    if form.is_valid():
        form.save()
        return redirect('manage_results')
    return render(request, 'dashboard/edit_result.html', {'form': form, 'results': results})

@login_required
def delete_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    result.delete()
    return redirect('manage_results')


@login_required
def manage_highlights(request):
    highlights = HighlightPost.objects.all().order_by('-posted_on')
    if request.method == 'POST':
        form = HighlightPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_highlights')
    else:
        form = HighlightPostForm()
    return render(request, 'dashboard/manage_highlights.html', {
        'form': form,
        'highlights': highlights
    })

@login_required
def edit_highlight(request, highlight_id):
    highlight = get_object_or_404(HighlightPost, id=highlight_id)
    form = HighlightPostForm(request.POST or None, instance=highlight)
    if form.is_valid():
        form.save()
        return redirect('manage_highlights')
    return render(request, 'dashboard/edit_highlight.html', {'form': form, 'highlight': highlight})

@login_required
def delete_highlight(request, highlight_id):
    highlight = get_object_or_404(HighlightPost, id=highlight_id)
    highlight.delete()
    return redirect('manage_highlights')



