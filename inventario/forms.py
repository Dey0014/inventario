from django import forms
from django.contrib.auth.models import User, Group

    
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