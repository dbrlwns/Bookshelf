from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from jazz.forms import JazzForm
from jazz.models import AudioTransformJob
from jazz.services import set_duration, mix_jazz_loop, analyze_bpm
from jazz.tasks import transform_jazz_task


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
    jazz.style = request.POST.get("style", jazz.style)
    jazz.status = "processing"
    jazz.save(update_fields=["style", "status"])

    # mix_jazz_loop(jazz)
    transform_jazz_task.delay(jazz.id) # redis의 작업 큐에 작업 메시지 삽입
    return redirect('jazz:jazz_detail', id=id) # trailing slash
