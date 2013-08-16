#-*- coding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets
from django.forms import ModelForm
from models import Foto, Galeria, UploadArquivo
        
class FormAdminArquivo(ModelForm):
    class Meta:
        model = UploadArquivo
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data['arquivo']
        arquivo_nome = self.cleaned_data['arquivo'].name
        if not arquivo_nome.endswith(".zip"):
            raise forms.ValidationError(u'O arquivo selecionado não possui a extensão .zip')
   #     if not arquivo._size < 10485760:
   #         raise forms.ValidationError(u'O arquivo selecionado tem que ter menos de 10.0MB de tamanho.')
        return self.cleaned_data['arquivo']    

class FormAdminGaleria(ModelForm):   
    fotos = forms.ModelMultipleChoiceField(Foto.objects.all())
    
    class Meta:
        model = Galeria

    def __init__(self, *args, **kwargs):
        super(FormAdminGaleria, self).__init__(*args, **kwargs)
        self.fields['fotos'] = forms.ModelMultipleChoiceField(Foto.objects.all(),
            widget = widgets.FilteredSelectMultiple(verbose_name = "Fotos", is_stacked = False), required = False)
        self.fields['arquivo'] = forms.ModelMultipleChoiceField(UploadArquivo.objects.all(),
            widget = widgets.FilteredSelectMultiple(verbose_name = "Arquivos", is_stacked = False), required = False, label="Arquivos")

class FormFoto(ModelForm):
    class Meta:
        model = Foto
        exclude = ['titulo', 'titulo_slug', 'descricao', 'ordem', 'data', 'data_editado', 'thumbnails', 'publicado', 'autor', 'upload']
    