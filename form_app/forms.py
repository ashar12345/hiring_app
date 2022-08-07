from django import forms
from django.contrib.auth.models import User

DOMAIN = [
('', 'Select'),
('data_science', 'DATA SCIENCE'),
('ui_ux', 'UI/UX'),

]

class DocumentForm(forms.Form):
    document = forms.FileField(label='Upload your resume in PDF format', widget=forms.FileInput(attrs={'accept':'application/pdf'}))
    domain = forms.CharField(label='Select your work domain', widget=forms.Select(choices=DOMAIN))
    exp_years = forms.IntegerField(required=True)
    salary = forms.IntegerField(required=True)
    exp_salary = forms.IntegerField(required=True)
    skillset = forms.CharField(label='Enter your technical skill(s) (comma seperated)', required=True)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')
