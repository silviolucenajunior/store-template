#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from modulos.galerias.models import Galeria


class Categoria(models.Model):
    categoria_pai = models.ForeignKey("Categoria", blank = True, null = True)
    prioridade = models.IntegerField("Prioridade", blank = True, null = True, default = 0)
    publicado = models.BooleanField(blank = True, help_text = u"Apenas categorias publicadas serão exibidas no site.")
    titulo = models.CharField(u"Titulo", max_length = 196, blank = False, null = True)
    titulo_slug = models.SlugField("Titulo Slug", blank = True, null = True)

    class Meta:
        verbose_name = u"Categoria"
        verbose_name_plural = u"Categorias"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def get_absolute_url(self):
        return "/produtos/categoria/%s" % self.titulo_slug


class Produto(models.Model):
    __miniaturas__ = (
       ("imagem", ("padrao", 240, 100)),
       ("imagem", ("galeria", 800, 600)),
    )
    autor = models.ForeignKey(User, blank = True, null = True, related_name = "produto_user")
    caracteristicas = models.CharField("Caracteristicas", max_length = 255, blank = True, null = True)
    codigo = models.CharField("Codigo", max_length = 255, blank = True, null = True)
    data_editado = models.DateTimeField("Editado em", auto_now = True, blank = True, null = True)
    data_criado = models.DateTimeField("Adicionado em", auto_now_add = True, blank = True, null = True)
    descricao = models.TextField(u"Descricao", max_length = 255, blank = False, null = True)
    galeria = models.ForeignKey(Galeria, blank = True, null = True)
    imagem = models.ImageField(u"Imagem", upload_to = 'img/novidades', blank = True, null = True)
    parcelas = models.IntegerField("Parcelas", blank = True, null = True, default = 2, help_text = "quantidade de parcelas para pagamento.")
    prioridade = models.IntegerField("Prioridade", blank = True, null = True, default = 0)
    publicado = models.BooleanField(help_text = u"Apenas novidades publicadas serão exibidas no site.")
    titulo = models.CharField(u"Titulo", max_length = 196, blank = False, null = True)
    titulo_slug = models.SlugField("Titulo Slug", blank = True, null = True)
    valor = models.FloatField("Valor", blank = True, null = True, default = 0)

    class Meta:
        verbose_name = u"Produto"
        verbose_name_plural = u"Produtos"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def get_absolute_url(self):
        return "/produtos/%s" % self.titulo_slug


