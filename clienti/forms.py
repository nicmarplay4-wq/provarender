from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Appuntamento, Cliente

class AppuntamentoForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, label="Nome")
    cognome = forms.CharField(max_length=100, label="Cognome")
    email = forms.EmailField(label="Email")
    telefono = forms.CharField(max_length=20, label="Telefono")
    
    class Meta:
        model = Appuntamento
        fields = ['data_ora', 'tipo_consulenza', 'note']
        widgets = {
            'data_ora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'note': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='form-group col-md-6 mb-3'),
                Column('cognome', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('telefono', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('data_ora', css_class='form-group col-md-6 mb-3'),
                Column('tipo_consulenza', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('note', css_class='mb-3'),
            Submit('submit', 'Prenota Appuntamento', css_class='btn btn-primary btn-lg')
        )
    
    def save(self, commit=True):
        cliente, created = Cliente.objects.get_or_create(
            email=self.cleaned_data['email'],
            defaults={
                'nome': self.cleaned_data['nome'],
                'cognome': self.cleaned_data['cognome'],
                'telefono': self.cleaned_data['telefono'],
            }
        )
        appuntamento = super().save(commit=False)
        appuntamento.cliente = cliente
        if commit:
            appuntamento.save()
        return appuntamento
