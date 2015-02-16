from django.forms import ModelForm
from django import forms
from models import Denuncia

class DenunciaForm(ModelForm):
	 class Meta:
		 model = Denuncia
		 fields = ['tipo', 'numero', 'screenshot', 'desc']
		#  widgets = {
		# 	'numero': forms.TextInput(attrs={'class': '.pure-skin-light .pure-form input'}),
		# }