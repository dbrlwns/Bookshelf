from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from jazz.forms import JazzForm
from jazz.models import AudioTransformJob
from jazz.services import transformToJazz, set_duration, mix_jazz_loop, analyze_bpm


# Create your views here.
def jazz_home(request):
    forms = JazzForm()
    works = AudioTransformJob.objects.all()
    return render(request, 'jazz/jazzHome.html', {'forms': forms, 'works': works})


@require_POST
def jazz_add(request):
    form = JazzForm(request.POST, request.FILES)
    if form.is_valid():
        jazz = form.save()
        set_duration(jazz, jazz.original_file.path) # duration 갱신
        analyze_bpm(jazz) # 추후 celery로 task 분리
    return redirect('/jazz/')


def jazz_detail(request, id):
    form = JazzForm(request.POST, request.FILES)
    jazz = AudioTransformJob.objects.get(id=id)
    return render(request, "jazz/jazzDetail.html", {'form': form, 'jazz': jazz})


@require_POST
def jazz_transform(request, id):
    jazz = AudioTransformJob.objects.get(id=id)
    # result = transformToJazz(jazz)  # 변환
    jazz.style = request.POST.get("style", jazz.style)
    jazz.save(update_fields=["style"])

    mix_jazz_loop(jazz)
    return redirect(f'/jazz/{id}')

