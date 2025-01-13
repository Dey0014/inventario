from .models import *
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
    
class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    email = forms.EmailField(label="Correo Electrónico")
    tipo_usuario = forms.ChoiceField(choices=[('Coordinador', 'Coordinador'), ('Analista', 'Analista')], label="Tipo de Usuario")
    
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'tipo_usuario']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data