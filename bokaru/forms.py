from django import forms


class Register(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.PasswordInput()
