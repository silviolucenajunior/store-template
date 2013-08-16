#-*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.contrib import admin
from forms import FormFoto
from middleware.upload_handler import UploadProgressCachedHandler
from models import Foto, Galeria
from galerias.template_tags.index_gallery_tags import pegar_miniatura
from utilidades.imagem import handler_upload_foto, criar_miniatura


from django.core.urlresolvers import get_urlconf, clear_url_caches
from django.utils.importlib import import_module

from django.conf.urls.defaults import *

from django.core import management
from django.core.management import sql, color
from django.db import connections, models



from django.db.models import get_models
from django.db.models.loading import load_app

#Importa a biblioteca grafica do Python (PIL - Python Imaging Library)
try:
    import Image
except ImportError:
    try:
        from modulos.PIL import Image
    except ImportError:
        raise ImportError(u"Index Gallery não conseguiu importar a biblioteca de imagem do Pytho (Python Imaging Library).")


#Views Plugin TinyMCE

def instalar_plugin(request):
    conteudo_arquivo = """aplicacoes = (
    'django.contrib.auth',
    'third_party.grappelli',
    'third_party.djblets',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.syndication',
    'django.contrib.messages',
    'modulos.catalogo',
    'modulos.cinema',
    'modulos.configuracao',
    'modulos.disco_virtual',
    'modulos.index_enquete',
    'modulos.index_evento',
    'modulos.index_gallery',
    'modulos.newsletter',
    'modulos.noticia',
    'modulos.novidades',
    "modulos.onde_encontrar",
    'modulos.paginas',
    'modulos.popup',
    'modulos.produtos',
    'modulos.sociable',
    'modulos.tags',
    'modulos.scrum',
    'third_party.debug_toolbar',
    'third_party.tagging',

)"""
    caminho_xml = "%s/../plugins_instalados.py" % settings.MEDIA_ROOT
    arquivo_xml = open(caminho_xml, "w")
    arquivo_xml.write(unicode(conteudo_arquivo).encode('utf-8'))
    arquivo_xml.close()
    return HttpResponse("Instalado")
    app = load_app("modulos.noticia")
    admin_teste = import_module("modulos.noticia.admin")
    connection = connections["default"]
    cursor = connection.cursor()
    style = color.no_style()
    sql_tabelas = sql.sql_create(app, style, connection)
  #  for sql_query in sql_tabelas:
      #  cursor.execute(sql_query)
    varaveis = import_module(get_urlconf())

    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()

    #varaveis.urlpatterns = patterns('',
    #(r'^admin/configuracao/', include('modulos.configuracao.admin_urls')),
    #(r'^admin/index_enquete/', include('modulos.index_enquete.admin_urls')),
    #(r'^admin/', include(admin.site.urls)),
    #(r'^disco_virtual/', include('modulos.disco_virtual.urls')),
    #(r'^onde-encontrar/', include('modulos.onde_encontrar.urls')),
    #(r'^enquete/', include('modulos.index_enquete.urls')),
    #(r'^eventos/', include('modulos.index_evento.urls')),
    #(r'^galerias/', include('modulos.index_gallery.urls')),
    #(r'^grappelli/', include('grappelli.urls')),
    #(r'^newsletter/', include('modulos.newsletter.urls')),
    #(r'^popup/', include('modulos.popup.urls')),
    #(r'^noticia/', include('modulos.noticia.urls')),
    #(r'^utils/', include('modulos.utils.urls')),
    #(r'^site_media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),


#)
    return HttpResponse("Instalado")



def teste_banco(request):

    app = load_app("modulos.noticia")
    app = import_module("modulos.noticia.admin")
    raise Exception(app)
    connection = connections["default"]
    style = color.no_style()
    criar = sql.sql_create(app, style, connection)
    raise Exception(criar)
    raise Exception(path)
    cor = color.no_style
    model = import_module("modulos.noticia.models")


    cursor = connection.cursor()
    statements, pending = sql.sql_model_create(model, style)



#View usada pelo Plugin TinyMCE para upload e inserção de foto no texto
def cadastrar_foto_plugin_view(request):
    variaveis = RequestContext(request)
    return render_to_response('index_gallery/plugin_tiny_foto.html', variaveis)

#View usada pelo Plugin TinyMCE para upload e inserção de foto no texto
def cadastrar_foto_plugin_ajax(request):
    dados_resposta = {"sucesso": 0}
    if request.method == "POST":
        formulario = FormFoto(request.POST, request.FILES)
        foto = formulario.save()
        foto.adicionar_miniaturas_padrao()
        #foto.criar_miniaturas()
        dados_resposta = {
            "sucesso": 1,
            "tamanho": (foto.imagem.width, foto.imagem.height),
            "imagem_original": "%s%s" % (settings.MEDIA_URL, foto.imagem),
            "imagem_pequeno": pegar_miniatura(foto, "foto-tiny-plugin-pequena"),
            "imagem_medio": pegar_miniatura(foto, "foto-tiny-plugin-media"),
            "imagem_grande": pegar_miniatura(foto, "foto-tiny-plugin-grande"),
        }
    return HttpResponse(simplejson.dumps(dados_resposta))



#==============================================================



#Adiciona a foto para galeria selecionada (Drag & Drop)
def adicionar_foto_galeria_ajax(request, id_foto, id_galeria):
    foto = Foto.objects.get(id = id_foto)
    galeria = Galeria.objects.get(id = id_galeria)
    galeria.fotos.add(foto)
    galeria.save()
    return HttpResponse("true");

#Cadastra uma nova galeria e adiciona todas as fotos vindas via post à galeria
def cadastrar_galeria(request):
    galeria = Galeria()
    galeria.save()
    for foto_id in request.POST.getlist('foto'):
        foto = Foto.objects.get(id = int(foto_id))
        galeria.fotos.add(foto)
    galeria.save()
    return HttpResponseRedirect("/galerias/visualizar_galeria/%s" % galeria.id)

#Deleta a foto via ajax
def deletar_foto_ajax(request, id_foto):
    try:
        foto = Foto.objects.get(id = int(id_foto))
        foto.delete()
    except Foto.DoesNotExist:
        pass
    return HttpResponse("true")

def fotos_json(request):
    fotos_galeria = {}
    for foto in Foto.objects.all():
        fotos_galeria[foto.id] = []
        for galeria in foto.galeria_foto.all():
            fotos_galeria[foto.id].append(galeria.id)
    return HttpResponse(simplejson.dumps(fotos_galeria))

def gerenciador_view(request):
    galerias = Galeria.objects.all()
    fotos = Foto.objects.all()
    variaveis = RequestContext(request, {'galerias': galerias, 'fotos': fotos})
    return render_to_response('index_gallery/gerenciar.html', variaveis)

#Listar todas as galerias
def listar_galerias_view(request):
    galerias = Galeria.objects.all()
    variaveis = RequestContext(request, {'galerias': galerias})
    return render_to_response('index_gallery/listar_galerias.html', variaveis)

#View usada para visualizar a pagina de manipulação de fotos e para cropar uma foto.
def manipular_foto_view(request, foto) :
    obj_foto = Foto.objects.get(id = foto)
    thumbnails = obj_foto.thumbnails.all()
    if request.method == "POST" :
        crop_dimensao = (int(request.POST['x']), int(request.POST['y']), int(request.POST['x2']), int(request.POST['y2']))
        imagem_caminho = "%s/%s" % (settings.MEDIA_ROOT, obj_foto.arquivo)
        imagem = Image.open(imagem_caminho)
        imagem_crop = imagem.crop(crop_dimensao)
        imagem_crop.save(imagem_caminho, imagem.format)
        obj_foto.save()
        obj_foto.criar_miniaturas()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    variaveis = RequestContext(request, {'foto': obj_foto, 'thumbnails': thumbnails, "idObjeto":obj_foto.id})
    return render_to_response('index_gallery/crop.html', variaveis)

#View usada para redimensionar uma foto
def redimensionar_foto_view(request, foto):
    obj_foto = Foto.objects.get(id = foto)
    thumbnails = obj_foto.thumbnails.all()
    if request.method == "POST":
        altura = int(request.POST['alturaField'])
        largura = int(request.POST['larguraField'])
        imagem_caminho = "%s/%s" % (settings.MEDIA_ROOT, obj_foto.arquivo)
        imagem = Image.open(imagem_caminho)
        imagem_resize = imagem.resize((largura, altura))
        imagem_resize.save(imagem_caminho, imagem.format)
        obj_foto.save()
        obj_foto.criar_miniaturas()
    variaveis = RequestContext(request, {'foto': obj_foto, 'thumbnails': thumbnails, "idObjeto":obj_foto.id})
    return render_to_response('index_gallery/manipular_foto_padrao.html', variaveis)

def setar_ordem_foto_ajax(request, id_foto, nova_ordem):
    foto = Foto.objects.get(id = id_foto)
    foto.ordem = nova_ordem
    foto.save()
    return HttpResponse("true")

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    data = cache.get(123456)
    return HttpResponse(data)

#Retorna uma pagina html usada para visualizar a galeria que possui o id passado na url
def visualizar_galeria_view(request, galeria_id):
    try:
        galeria = Galeria.objects.get(id = galeria_id)
        variaveis = RequestContext(request, {'galeria': galeria})
    except Galeria.DoesNotExist:
        variaveis = RequestContext(request, {'galeria': None})
    return render_to_response('index_gallery/galeria.html', variaveis)

#Retorna uma pagina html usada para visualizar a previa da galeria que possui o id passado na url
def visualizar_galeria_previa_view(request, galeria_id):
    try:
        galeria = Galeria.objects.get(id = galeria_id)
        variaveis = RequestContext(request, {'galeria': galeria})
    except Galeria.DoesNotExist:
        variaveis = RequestContext(request, {'galeria': None})
    return render_to_response('index_gallery/galeria_preview.html', variaveis)

#Retorna uma pagina html contendo todas as galerias de determinado autor
def visualizar_galerias_por_autor_view(request, autor_username):
    galerias = Galeria.objects.filter(autor__username = autor_username).all()
    variaveis = RequestContext(request, {'galerias': galerias})
    return render_to_response('index_gallery/galerias_por_autor.html', variaveis)

#Retorna uma pagina html contendo todas as galerias de determinada categoria
def visualizar_galerias_por_categoria_view(request, categoria_slug):
    galerias = Galeria.objects.filter(categoria__titulo_slug = categoria_slug).all()
    variaveis = RequestContext(request, {'galerias': galerias})
    return render_to_response('index_gallery/galerias_por_autor.html', variaveis)

#Retorna uma pagina html contendo todas as galerias de determinada autor em determinada categoria
def visualizar_galerias_por_categoria_autor_view(request, categoria_slug, autor_username):
    galerias = Galeria.objects.filter(categoria__titulo_slug = categoria_slug).filter(autor__username = autor_username).all()
    variaveis = RequestContext(request, {'galerias': galerias})
    return render_to_response('index_gallery/galerias_por_autor.html', variaveis)