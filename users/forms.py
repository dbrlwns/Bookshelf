from django import forms

from users.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=3, max_length=30,
        widget=forms.TextInput(attrs={
            'class' : 'login-form form-control',
            'placeholder' : '아이디 입력'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class' : 'password-form form-control',
            'placeholder' : '비밀번호 입력'}))


class SignupForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=15, widget=forms.TextInput(attrs={
        'class' : 'login-form form-control form-label',
    }))
    password1 = forms.CharField(label="비밀번호" , widget=forms.PasswordInput(attrs={
        'class' : 'login-form form-control form-label',
    }))
    password2 = forms.CharField(label="비밀번호 재입력", widget=forms.PasswordInput(attrs={
        'class' : 'login-form form-control form-label',
    }))


class RevisionForm(forms.ModelForm):
    # 모델 필드가 아닌 추가 검증/위젯 설정이 필요하면 여기서 선언.
    # 다만 required 설정을 명확히 하자. 기본값이 True로 비어있으면 is_valid가 False가 됨.
    first_name = forms.CharField(required=False, min_length=1)
    last_name = forms.CharField(required=False, min_length=1)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "profile_image"]
