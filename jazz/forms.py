from pathlib import Path
from django import forms

from jazz.models import AudioTransformJob


class JazzForm(forms.ModelForm):
    class Meta:
        model = AudioTransformJob
        fields = ("original_file",)
        widgets = {"original_file": forms.FileInput(attrs={"class": "form-control", "accept": ".wav, .mp3, .m4a"})}

    def clean_original_file(self):
        original_file = self.cleaned_data["original_file"]
        allowed_extensions = (".wav", ".mp3", ".m4a")
        extension = Path(original_file.name).suffix.lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError("only wav, mp3 and m4a supported")

        max_size = 20 * 1024 * 1024 # 20mb
        if original_file.size > max_size:
            raise forms.ValidationError("file too large, under 20mb")

        return original_file