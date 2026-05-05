from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from jazz.forms import JazzForm


# Create your views here.
def jazz_home(request):
    forms = JazzForm()
    return render(request, 'jazz/jazzHome.html', {'forms': forms})

@require_POST
def jazz_add(request):
    form = JazzForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
    return redirect('/jazz/')