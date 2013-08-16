#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

class Novidade(models.Model):
    TIPOS_ABRIR = (
        ("mesma", "Mesma Janela"),
        ("fancy", "Fancy Box"),
        ("outra", "Outra Janela")
    )
    __miniaturas__ = (
       ("imagem", ("padrao", 627, 297)),
    )
    __crop__ = {
        "largura": 627,
        "altura": 297,
        "proporcao": "2.11",
        "manter_original": True
    }

    abrir_em = models.CharField("Abrir em", choices = TIPOS_ABRIR, max_length = 255, blank = True, null = True)
    autor = models.ForeignKey(User, blank = True, null = True, related_name = "novidade_user")
    data_editado = models.DateTimeField("Editado em", auto_now = True, blank = True, null = True)
    data_criado = models.DateTimeField("Adicionado em", auto_now_add = True, blank = True, null = True)
    descricao = models.TextField(u"Descricao", max_length = 255, blank = False, null = True)
    imagem = models.ImageField(u"Imagem", upload_to = 'img/novidades', blank = True, null = True)
    link = models.URLField(u"Link", blank = True, null = True)
    prioridade = models.IntegerField("Prioridade", blank = True, null = True, default = 0)
    publicado = models.BooleanField(blank = True, help_text = u"Apenas novidades publicadas serão exibidas no site.")
    titulo = models.CharField(u"Titulo", max_length = 196, blank = False, null = True)

    class Meta:
        verbose_name = u"Novidade"
        verbose_name_plural = u"Novidades"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def get_absolute_url(self):
        return "%s" % self.link



