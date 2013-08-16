#-*- coding: utf-8 -*-
import os

from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

from django.template.defaultfilters import slugify

from django.utils.html import escape, conditional_escape

class CustomImageWidget(ClearableFileInput):   
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            diretorio, imagem = os.path.split(value.url) #Modificacao Silvio Lucena Junior
            caminho_thumbnail = "%s/thumbnails/admin_%s_%s" % (diretorio, name, imagem) #Modificacao Silvio Lucena JUnior
            #Modificacao Silvio Lucena Junior             
            conteudo_html = """ 
                <a href="%s" class="fancy-trigger">
                    <img src="%s" id="%s" /> 
                </a>
                <a class="fancy-crop" href="cropar/%s?modal=true">Recortar</a>
            """ % (escape(value.url), escape(force_unicode(caminho_thumbnail)), slugify(escape(value)), escape(value))
            substitutions['initial'] = (conteudo_html)
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
    