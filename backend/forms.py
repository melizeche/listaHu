from django.forms import ModelForm
from django import forms
from models import Denuncia

class DenunciaForm(ModelForm):
	 class Meta:
		model = Denuncia
		fields = ['tipo', 'numero', 'screenshot', 'desc']
		widgets = {
			'numero': forms.TextInput(attrs={'style': 'width:90%', 'placeholder':'0981XXXXXX'}),
			'screenshot': forms.FileInput(attrs={'style': 'width:100%'}),
			'desc': forms.Textarea(attrs={'style': 'width:90%'}),
			}