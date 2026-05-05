from django import forms

from jazz.models import AudioTransformJob


class JazzForm(forms.ModelForm):
    class Meta:
        model = AudioTransformJob
        fields = ("original_file",)