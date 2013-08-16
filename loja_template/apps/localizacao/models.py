#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

class Estado(models.Model):
    titulo = models.CharField("Titulo", max_length = 255, blank = True, null = True)
    titulo_slug = models.SlugField("Titulo Slug", blank = True, null = True)

    class Meta:
        verbose_name = u"Estado"
        verbose_name_plural = u"Estados"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

class Cidade(models.Model):
    estado = models.ForeignKey(Estado, blank = True, null = True)
    titulo = models.CharField("Titulo", max_length = 255, blank = True, null = True)
    titulo_slug = models.SlugField("Titulo Slug", blank = True, null = True)

    class Meta:
        verbose_name = u"Cidade"
        verbose_name_plural = u"Cidades"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

class Localizacao(models.Model):
    cidade = models.ForeignKey(Cidade, related_name = "localizacoes",  blank = False, null = False)
    titulo = models.CharField("Titulo", max_length = 255, blank = True, null = True)
    titulo_slug = models.SlugField("Titulo Slug", max_length = 255, blank = True, null = True)

    class Meta:
        verbose_name = u"Localizacão"
        verbose_name_plural = u"Localizacões"

    def __str__(self) :
        return "%s - %s" % (self.cidade.titulo, self.titulo)

    def __unicode__(self) :
        return u"%s - %s" % (self.cidade.titulo, self.titulo)
        

