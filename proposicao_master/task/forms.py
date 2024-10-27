from django import forms
from .models import Jogador


class JogadorForm(forms.ModelForm):
    class Meta:
        model = Jogador
        fields = ['nome']  # Só queremos capturar o nome no início
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'})
        }
