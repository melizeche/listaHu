# -*- encoding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from models import Denuncia

error_numero = {
    'min_length': 'No se aceptan números cortos, uno puede desuscribirse de estos numeros contactando con su telefónica, '
                  'introducí en al menos 10 caracteres, ej. 09XXXXXXXX'
}
error_screen = {
    'required': 'Es obligatorio agregar la captura de pantalla'
}


class DenunciaForm(ModelForm):
    numero = forms.CharField(
        min_length=10, max_length=15, error_messages=error_numero,
        widget=forms.TextInput(
            attrs={'style': 'width:90%', 'placeholder': '0981XXXXXX', 'class': 'pure-form'}),
        help_text="Podes ingresar como 09XXXXXXXX, 5959XXXXXXXX o +5959XXXXXXXX")
    screenshot = forms.ImageField(error_messages=error_screen,
                                  widget=forms.FileInput(
                                      attrs={'style': 'width:100%'}),
                                  help_text="Si fue una llamada hacer captura del registro de llamadas")

    class Meta:
        model = Denuncia
        fields = ['tipo', 'numero', 'screenshot', 'desc']
        widgets = {
            'numero': forms.TextInput(attrs={'style': 'width:90%', 'placeholder': '0981XXXXXX'}),
            'screenshot': forms.FileInput(attrs={'style': 'width:100%'}),
            'desc': forms.Textarea(attrs={'style': 'width:90%'}),
        }
