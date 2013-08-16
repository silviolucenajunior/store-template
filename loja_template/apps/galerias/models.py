#-*- coding: utf-8 -*-
from cStringIO import StringIO
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from utilidades.imagem import criar_miniatura
import os
import zipfile

#Importa a biblioteca grafica do Python (PIL - Python Imaging Library)
try:
    import Image
except ImportError:
    try:
        from PIL import Image
    except ImportError:
        raise ImportError(u"Index Gallery não conseguiu importar a biblioteca de imagem do Pytho (Python Imaging Library).")

#Classe usada para representar uma categoria para uma galeria
class Categoria(models.Model):
    titulo = models.CharField(max_length = 96, unique = True, blank = False, null = True, help_text = "")
    titulo_slug = models.SlugField(unique = True, blank = False, null = True, help_text = "")
    descricao = models.TextField(u"Descrição", blank = True, null = True)

    def __str__(self):
        return u"%s" % self.titulo

    def __unicode__(self):
        return u"%s" % self.titulo

#Classe usada para representar um conjunto de configurações usadas para cropar uma imagem
class Crop(models.Model):
    titulo = models.CharField(max_length = 96, unique = True, blank = False, null = True, help_text = "")
    largura = models.IntegerField("Largura", blank = False, null = True, help_text = "")
    altura = models.IntegerField("Altura", blank = False, null = True, help_text = "")
    proporcional = models.BooleanField(u"Proporcional")
    redimensionar = models.BooleanField(u"Redimensionar")

    def __str__(self):
        return u"%s" % self.titulo

    def __unicode__(self):
        return u"%s" % self.titulo

    def fator_proporcao(self):
        if self.proporcional:
            return str((self.largura * 1.0) / self.altura)[:4]
        return 0.3

#Cada objeto desta classe representa um arquivo de imagem e esta associado a um arquivo no disco.
class Foto(models.Model) :
    """Classe que guardar os dados referentes a um arquivo de imagem tal como nome, caminho, thumbnails e damais
    dados pertinentes a uma foto."""
    titulo = models.CharField(u"Nome", max_length = 196, unique = True, blank = True, null = True)
    titulo_slug = models.SlugField(u"Slug", help_text = "", max_length = 196, unique = True, blank = True, null = True)
    descricao = models.TextField(u"Descrição", help_text = u"Pequeno texto descritivo da foto.", blank = True, null = True)
    ordem = models.IntegerField(default = 0, help_text = u"Indica a ordem da foto dentro da galeria.", blank = True, null = True)
    imagem = models.ImageField("Imagem", upload_to = "galerias", help_text = "", blank = True, null = True)
    upload = models.ForeignKey("UploadArquivo", related_name = "foto_upload_arquivo", blank = True, null = True)
    thumbnails = models.ManyToManyField("Tamanho", help_text = "", related_name = "foto_tamanho", verbose_name = u"Tamanhos", blank = True, null = True)
    data_criado = models.DateTimeField(u"Adicionada em", auto_now_add = True, null = True, blank = True)
    data_editado = models.DateTimeField(u"Editado em", auto_now = True, null = True, blank = True)
    publicado = models.BooleanField(help_text = "")
    autor = models.ForeignKey(User, related_name = "foto_user", blank = True, null = True)

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"
        ordering = ['ordem']

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    #Adiciona todas a miniaturas marcadas como padrão a foto.
    def adicionar_miniaturas_padrao(self):
        for padrao in Tamanho.objects.filter(padrao = True):
            if not padrao in self.thumbnails.all():
                self.thumbnails.add(padrao)
        self.save()
        self.criar_miniaturas()

    #Calcula o tamanho da imagem para ser mostrada no admin.
    def admin_tamanho(self):
        tamanho = ""
        try:
            if self.imagem.size < 1000:
                tamanho = str(self.imagem.size) + "&nbsp;B"
            elif self.imagem.size >= 1000 and self.imagem.size < 1000000:
                tamanho = str(self.imagem.size/1000) + "&nbsp;kB"
            elif self.imagem.size >= 1000000:
                tamanho = str(self.imagem.size/1000000) + "&nbsp;MB"
        except Exception:
            tamanho = "Arquivo deletado do servidor."
        return mark_safe(tamanho)
    admin_tamanho.short_description = "Tamanho do arquivo"
    admin_tamanho.allow_tags = True

    #Mostra a miniatura da foto no admin.
    def admin_thumbnail(self) :
        return u'<a href="%s%s%s" class="fancy-trigger"><img src="%s%sthumbnails/admin_%s"/></a>' % \
    (settings.MEDIA_URL, "img/galerias/", os.path.basename(self.imagem.name), \
     settings.MEDIA_URL, "img/galerias/", os.path.basename(self.imagem.name))
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True

    def criar_miniaturas(self):
        if self.imagem:
            admin_thumbnail_path = "%s/%sthumbnails/admin_%s" % (settings.MEDIA_ROOT, "img/galerias/", os.path.basename(self.imagem.name))
            criar_miniatura(self.imagem.path, (32, 32), admin_thumbnail_path, False)
            for tamanho in self.thumbnails.all():
                thumbnail_path = "%s/%sthumbnails/%s_%s" % (settings.MEDIA_ROOT, "img/galerias/", slugify(tamanho.titulo), os.path.basename(self.imagem.name))
                criar_miniatura(self.imagem.path, (tamanho.largura, tamanho.altura), thumbnail_path, tamanho.proporcional)

    #Deleta todas as miniaturas criadas para a foto
    def deletar_miniaturas(self):
        try:
            for tamanho in self.thumbnails.all() :
                thumbnail_dir = "%s/%sthumbnails/" % (settings.MEDIA_ROOT, "img/galerias/")
                thumbnail_file = "%s_%s" % (slugify(tamanho.titulo), os.path.basename(self.imagem.name))
                for arquivo in os.listdir(thumbnail_dir) :
                    if arquivo == thumbnail_file :
                        os.unlink("%s%s" % (thumbnail_dir, thumbnail_file))
            thumbnail_dir = "%s/%sthumbnails/" % (settings.MEDIA_ROOT, "img/galerias/")
            thumbnail_file = "admin_%s" % (os.path.basename(self.imagem.name))
            os.unlink("%s%s" % (thumbnail_dir, thumbnail_file))
        except:
            pass

    def get_absolute_url(self):
        return "/galerias/foto/%s" % self.titulo_slug

    def pegar_miniatura(self, nome_miniatura):
        miniatura = Tamanho.objects.get(titulo = nome_miniatura)
        return "%sthumbnails/%s_%s" % ("img/galerias/", slugify(miniatura.titulo), os.path.basename(self.imagem.name))

#Cada objeto desta classe representa uma galeria de fotos.
class Galeria(models.Model) :
    """Descricao da classe Galeria"""
    titulo = models.CharField("Nome", max_length = 96, help_text = "", unique = True, blank = False, null = True)
    titulo_slug = models.SlugField(u"Slug", help_text = "", unique = True, blank = True, null = True)
    descricao = models.TextField(u"Descrição", help_text = u"Pequeno texto descritivo da galeria.", blank = True, null = True)
    categoria = models.ForeignKey(Categoria, related_name = "galeria_categoria", blank = True, null = True)
    capa = models.ImageField("Capa", upload_to = "img/galerias/" + 'capas', help_text = "", blank = True, null = True)
    fotos = models.ManyToManyField(Foto, related_name = "galeria_foto", verbose_name = "Fotos", blank = True, null = True, help_text = "Digite no campo busca para filtrar os resultados.")
    arquivos = models.ManyToManyField("UploadArquivo", blank = True, null = True, verbose_name = "Arquivos", help_text = "Digite no campo busca para filtrar os resultados.")
    data_criado = models.DateTimeField(u"Adicionada em", auto_now_add = True, null = True, blank = True)
    data_editado = models.DateTimeField(u"Editado em", auto_now = True, null = True, blank = True)
    publicado = models.BooleanField(help_text = u"Galerias publicas são visiveis para todos os usuarios.")
    autor = models.ForeignKey(User, related_name = "galeria_user", blank = True, null = True)

    class Meta:
        verbose_name = "Galeria"
        verbose_name_plural = "Galerias"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    def adicionar_arquivos(self):
        if self.arquivos.all():
            for arquivo_upload in self.arquivos.all():
                for foto in Foto.objects.filter(upload = arquivo_upload):
                    self.fotos.add(foto)
            self.save()

    def criar_miniaturas(self):
        self.criar_miniatura_capa()

    def criar_miniatura_capa(self):
        foto = Image.open(self.capa.path)
        dimensoes = (128, 128)
        thumbnail = foto.resize(dimensoes, Image.ANTIALIAS)
        thumbnail.save(self.capa.path, foto.format)

    def criar_zip(self):
        arquivo_zip = zipfile.ZipFile("/home/silvio/Documentos/temp.zip", "w")
        for foto in self.fotos.all():
            arquivo = "%s/%s" %(settings.MEDIA_ROOT, foto.imagem)

            arquivo_zip.write(arquivo, foto.imagem.name.split("/")[-1])
        arquivo_zip.close()

#Cada objeto desta classe representa um tamanho de thumbnail que pode ser gerado de cada foto.
class Tamanho(models.Model):
    """Classe que guardar os dados referentes as dimenções de thumbnail da foto, cada foto pode ter mais
    de um thumbnail"""
    titulo = models.CharField(u"Nome", max_length = 128, help_text = "", blank = False, null = True, unique = True)
    largura = models.IntegerField(u"Largura", help_text = "", blank = False, null = True)
    altura = models.IntegerField(u"Altura", help_text = "", blank = False, null = True)
    proporcional = models.BooleanField(u"Proporcional", help_text = u"Mantem a proporção da imagem original.")
    padrao = models.BooleanField(u"Padrão", help_text = u"Tamanhos padrão serão aplicados em todas as fotos.")

    class Meta:
        verbose_name = "Tamanho"
        verbose_name_plural = "Tamanhos"

    def __str__(self) :
        return "%s" % self.titulo

    def __unicode__(self) :
        return u"%s" % self.titulo

    #Usado para adicionar uma miniatura padrão a todas as fotos adicionadas a index gallery.
    def adicionar_para_fotos(self):
        for foto in Foto.objects.all():
            if foto.thumbnails:
                if not self in foto.thumbnails.all():
                    foto.thumbnails.add(self)
                    foto.criar_miniaturas()

#Classe para envior de arquivos zip contendo fotos.
class UploadArquivo(models.Model) :
    titulo = models.CharField(u"Nome", max_length = 96, help_text = "", unique = True, blank = False, null = True)
    usar_nome = models.BooleanField(u"Modificar nome", help_text = u"Caso marcado, as fotos terão o nome do upload seguido de um valor númerico sequencial.")
    data_criado = models.DateTimeField(u"Adicionada em", auto_now_add = True, null = True, blank = True)
    data_editado = models.DateTimeField(u"Editado em", auto_now = True, null = True, blank = True)
    arquivo = models.FileField("Arquivo (zip)", upload_to = "img/galerias/" + '../arquivos')
    thumbnails = models.ManyToManyField(Tamanho, related_name = "upload_arquivo", verbose_name = "Tamanhos", blank = True, null = True)
    publicado = models.BooleanField(u"Publico", help_text = u"Arquivos publicos serão visiveis para todos os usuarios.")
    autor = models.ForeignKey(User, related_name = "uploadarquivo_user", blank = True, null = True)

    class Meta:
        verbose_name = "Arquivo"
        verbose_name_plural = "Arquivos"

    def __str__(self):
        return "%s" % self.titulo

    def __unicode__(self):
        return u"%s" % self.titulo

    #Calcula o tamanho do arquivo para se ser mostrado no admin.
    def admin_tamanho(self):
        tamanho = ""
        try:
            if self.arquivo.size < 1000:
                tamanho = str(self.arquivo.size) + "&nbsp;B"
            elif self.arquivo.size >= 1000 and self.arquivo.size < 1000000:
                tamanho = str(self.arquivo.size/1000) + "&nbsp;kB"
            elif self.arquivo.size >= 1000000:
                tamanho = str(self.arquivo.size/1000000) + "&nbsp;MB"
        except Exception:
            tamanho = "Arquivo deletado do servidor."
        return mark_safe(tamanho)
    admin_tamanho.short_description = "Tamanho do arquivo"
    admin_tamanho.allow_tags = True

    #Processa o arquivo zip e criar objetos do tipo Foto para cada arquivo de imagem
    def processar_zip(self, usuario):
        if os.path.isfile(self.arquivo.path): #Verifica se é um arquivo
            arquivo_zip = zipfile.ZipFile(self.arquivo.path) #Carrega o arquivo zip
            if arquivo_zip.testzip(): #Verifica se não há arquivos corrompidos
                raise Exception('O arquivo %s esta corrompido.' % bad_file)
            contador = 1
            for nome_arquivo in arquivo_zip.namelist(): #Percorrer todos os arquivos do zip com base no nome
                arquivo = arquivo_zip.read(nome_arquivo) #Ler o arquivo atual com base na iteração
                try:
                    testar_imagem = Image.open(StringIO(arquivo)) #Abri o arquivo de imagem
                    testar_imagem.load() #Aloca espaço na memoria para o arquivo de imagem
                    testar_imagem = Image.open(StringIO(arquivo)) #Abre novamente o arquivo para poder se usar o modo verify
                    testar_imagem.verify() #Verifica se o arquivo de imagem não esta quebrado
                except IOError:
                    continue
                if len(arquivo): #Verifica se o tamanho do arquivo em bytes é maior que zero
                    #O bloco try usado para verificar se o arquivo já existe, se não uma exception é lançadaa e criamos então o arquivo.
                    try:
                        if self.usar_nome:
                            nome_foto = "%s - %s" % (self.titulo, contador)
                            foto = Foto.objects.get(titulo = nome_foto)
                        else:
                            foto = Foto.objects.get(titulo = nome_arquivo)
                    except Foto.DoesNotExist:
                        if self.usar_nome:
                            nome_foto = "%s - %s" % (self.titulo, contador)
                        else:
                            nome_foto = nome_arquivo
                        nome_foto_slug = slugify(nome_foto)
                        foto = Foto(titulo = nome_foto,
                                    titulo_slug = nome_foto_slug,
                                    descricao = "",
                                    upload = self,
                                    autor = usuario,
                                    data_editado = datetime.now(),
                                    publicado = self.publicado
                            )
                        foto.imagem.save(nome_arquivo, ContentFile(arquivo))
                        foto.thumbnails = self.thumbnails.all()
                        foto.save()
                        foto.criar_miniaturas()
                    contador += 1
            arquivo_zip.close()

#---------------------------------------SIGNALS------------------------------------------------------------
#Signal post delete para apagar do disco rigido os arquivos de miniatura da foto
def post_delete_foto(signal, instance, sender, **kwargs):
    instance.deletar_miniaturas()

signals.pre_delete.connect(post_delete_foto, sender = Foto)