from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


INPUT = 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
INPUT_LIGHT = 'w-full px-4 py-2.5 rounded-lg border border-gray-200 text-gray-800 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white'


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT, 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'rounded border-gray-600 text-indigo-500 bg-gray-800'}))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)


class StyledPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Current password', widget=forms.PasswordInput(attrs={'class': INPUT_LIGHT}))
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'class': INPUT_LIGHT}))
    new_password2 = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(attrs={'class': INPUT_LIGHT}))
