#-*- coding: utf-8 -*-
import urllib, urllib2


from django.contrib.auth.models import User
from django.db import models

from modulos.galerias.models import Galeria

class Bairro(models.Model):
    cidade = models.ForeignKey("Cidade", verbose_name = "Cidade", blank = False, null = True)
    titulo = models.CharField("Titulo", max_length = 128, blank = True, null = True)
    titulo_slug = models.SlugField("Titulo Slug")

    class Meta:
        verbose_name = u"Bairro"
        verbose_name_plural = u"Bairros"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def get_absolute_url(self):
        return "/locais/%s/%s" % (self.cidade.titulo_slug, self.titulo_slug)

class Cidade(models.Model):
    titulo = models.CharField("Titulo", max_length = 128, blank = True, null = True)
    titulo_slug = models.SlugField("Titulo Slug")

    class Meta:
        verbose_name = u"Cidade"
        verbose_name_plural = u"Cidade"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def get_absolute_url(self):
        return "/locais/%s/" % self.titulo_slug

class Local(models.Model):
    __miniaturas__ = (
       ("imagem", ("padrao", 200, 150)),
    )

    autor = models.ForeignKey(User, blank = True, null = True, related_name = "local_user")
    bairro = models.ForeignKey(Bairro, blank = True, null = True)
    data_editado = models.DateTimeField("Editado em", auto_now = True, blank = True, null = True) 
    data_criado = models.DateTimeField("Adicionado em", auto_now_add = True, blank = True, null = True)
    email = models.EmailField("Email", blank = True, null = True)
    endereco = models.CharField(u"Endereço", max_length = 255, blank = True, null = True)
    gerente = models.CharField("Gerente", max_length = 255, blank = True, null = True)
    imagem = models.ImageField(u"Imagem", upload_to = 'img/locais', blank = True, null = True)
    latitude = models.FloatField("Latitude", blank = True, null = True, default = 0)
    longitude = models.FloatField("Longitude", blank = True, null = True, default = 0)
    publicado = models.BooleanField(blank = True, help_text = u"Apenas locais publicados serão exibidos no site.")
    telefone = models.CharField("Telefone", max_length = 255, blank = True, null = True)
    titulo = models.CharField(u"Titulo", max_length = 196, blank = False, null = True)
    titulo_slug =  models.SlugField("Titulo Slug", blank = False, null = True)
    
  
    class Meta:
        verbose_name = u"Loja"
        verbose_name_plural = u"Lojas"
            
    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo
    
    def get_absolute_url(self):
        return "/local/" % self.titulo_slug

    def pegar_coordenadas(self):
        q_string = u'%s, %s' % (self.endereco, self.bairro.cidade)
        data = {
            'q': q_string.encode('utf-8'),
            'output': 'csv',
            'key': "ABQIAAAAvDjVyyEeeRdwFXFHhnQaxhSL7X9eFkihBtf85CDE1ZBEpqznOxSdexQAkkAhOhnHrgry8oBLBX--XA"
        }
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}
        url = urllib.urlencode(data)
        request = urllib2.Request("http://maps.google.com/maps/geo?" + url, None, headers)
        pagina = urllib2.urlopen(request)
        corta = pagina.read().split(',')

        self.latitude = corta[2]
        self.longitude = corta[3]
        self.save()
    

        

