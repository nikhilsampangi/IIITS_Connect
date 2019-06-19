from django import forms
from django.contrib.auth.models import User
from authentication.models import Topic,SentFiles


class CreateTopic(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'


class Registration(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Password mismatch')
        return confirm_password


class PublishMessage(forms.Form):
    message = forms.CharField(max_length=100)


class PublishFile(forms.ModelForm):

    class Meta:
        model = SentFiles
        fields = '__all__'
