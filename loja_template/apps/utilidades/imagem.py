#-*- coding: utf-8 -*-
from django.db.models import get_app, get_model
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils import simplejson
import os
import sys
import urllib2

from django.core.paginator import Paginator

try:
    import Image
except ImportError:
    try:
        from PIL import Image
    except ImportError:
        raise ImportError((u"Crop não conseguiu importar a biblioteca de imagem do Python (Python Imaging Library)."))
    
    
def cropar_imagem_delegate_view(request, app_alias, model_alias, id_objeto, imagem):
    app = get_app(app_alias)
    model = get_model(app_alias, model_alias)
    objeto = model.objects.get(id = int(id_objeto))
    request.session["obj_crop"] = objeto
    return cropar_imagem_view(request, imagem, post_redirect = request.path + "../../../../../")

#View normalmente usada no response_add e response_change do ModelAdmin para cropar imagem.
def cropar_imagem_view(request, imagem_name, post_redirect = "../", largura = None, altura = None, proporcao = None, POST_DATA = False, crops = False, manter_original = False):
    if imagem_name:
        if request.method == "POST" and POST_DATA == False:
            manter_original = request.POST.get("manter_original", False)
            if "crops" in request.session:
                for crop in request.session["crops"]:
                    dimensao_crop = (int(request.POST['x-%s' % crop.id]), int(request.POST['y-%s' % crop.id]), int(request.POST['x2-%s' % crop.id]), int(request.POST['y2-%s' % crop.id]))
                    cropar_imagem("%s/%s" % (settings.MEDIA_ROOT, imagem_name), dimensao_crop, manter_original = manter_original, nome_crop = slugify(crop.titulo)) 
                del request.session['crops']    
            else:     
                cropar_imagem("%s/%s" % (settings.MEDIA_ROOT, imagem_name), (int(request.POST['x']), int(request.POST['y']),
                                         int(request.POST['x2']), int(request.POST['y2'])), manter_original = False)
            redirecionar = request.POST['redirect']
            request.session['obj_crop'].criar_miniaturas()
            request.session['obj_crop'] = None
            if request.is_ajax():
                diretorio, imagem = os.path.split(imagem_name)
                caminho_thumbnail = "%s%s/thumbnails/admin_%s" % (settings.MEDIA_URL, diretorio,  imagem)
                return HttpResponse(caminho_thumbnail)
            else:    
                return HttpResponseRedirect(redirecionar)
        
        variaveis = RequestContext(request, {"manter_original": manter_original, 'crops': crops, 'imagem_name': imagem_name, 'post_redirect': post_redirect, "largura": largura, "altura":altura, "proporcao": proporcao})
        if "crops" in request.session:
            return render_to_response('utils/crop_multi.html', variaveis)
        else:
            if request.GET.has_key("modal"):
                return render_to_response('utils/modal_crop_padrao.html', variaveis)
            else:    
                return render_to_response('utils/crop_padrao.html', variaveis)
    else:
        return HttpResponseRedirect(post_redirect)
    
#Funcao para cropar uma imagem.
def cropar_imagem(imagem_path, dimensao_crop, manter_original = False, nome_crop = "crop"):
    if imagem_path:   
        imagem = Image.open(imagem_path)       
        imagem_crop = imagem.crop(dimensao_crop)
        if manter_original:
            diretorio, imagem = os.path.split(imagem_path)
            path_crop = "%s/%s_%s" % (diretorio, nome_crop, imagem)
            imagem_crop.save(path_crop, imagem.format, quality = 95)
        else:    
            imagem_crop.save(imagem_path, imagem.format, quality = 95)
            
    
#Função para criação de miniaturas, substitui a thumbnails do modulo Imagem da PIL por ser mais flexivel    
def criar_miniatura(caminho_imagem, dimencoes, thumbnail_path, proporcional, forcar = False):     
        foto = Image.open(caminho_imagem)
        foto.load()
        largura, altura = dimencoes
        largura_original, altura_original = foto.size
        thumbnail_path = thumbnail_path
        if proporcional :
            nova_largura = (largura_original * altura) / altura_original
            nova_altura = (altura_original * largura) / largura_original
            dimencoes = (largura, nova_altura)
            thumb = foto.resize(dimencoes, Image.ANTIALIAS)
        else:
            if forcar:
                thumb = foto.resize(dimencoes, Image.ANTIALIAS)
            else:    
                if largura_original < altura_original:
                    nova_altura = (largura * altura_original) / largura_original
                    nova_largura = altura
                elif altura_original < largura_original:    
                    nova_largura = largura
                    nova_altura = (altura * largura_original) / largura
                else:
                    nova_largura = largura
                    nova_altura = altura
                nova_largura = (largura_original * altura) / altura_original
                nova_altura = (altura_original * largura) / largura_original
                if nova_largura < largura:
                    if nova_altura < altura:
                        pass
                    else:
                        nova_largura = largura
                        nova_altura = altura_original * nova_largura / largura_original
                elif nova_altura < altura:
                    nova_altura = altura
                    nova_largura = nova_altura * largura_original / altura_original                    
                dimencoes = (nova_largura, nova_altura)
                thumb = foto.resize(dimencoes, Image.ANTIALIAS)
                thumb = thumb.crop((((nova_largura - largura) / 2), ((nova_altura - altura) / 2), (((nova_largura - largura) / 2) + largura), (((nova_altura - altura) / 2) + altura)))
        thumb.save(thumbnail_path, foto.format, quality = 95) 
    
def paginacao(queryset, pagina = 1, ITEMS_POR_PAGINA = 2, LIMITE_DE_PAGINAS = 2):        
    items = None
    paginas = []
    paginacao_antes = False
    paginacao_apos = False
    paginacao = Paginator(queryset, ITEMS_POR_PAGINA)
    pagina_items = paginacao.page(int(pagina))
    if paginacao.num_pages > LIMITE_DE_PAGINAS * 2 + 1:
        if (int(pagina) - LIMITE_DE_PAGINAS <= 1):
            paginacao_antes = False
            paginas = [x for x in range(1, LIMITE_DE_PAGINAS * 2)]
        else :
            paginacao_antes = True
            paginas += [x for x in range(int(pagina) - 2, int(pagina) + 1)]            
        if (int(pagina) + LIMITE_DE_PAGINAS >= paginacao.num_pages):
            paginacao_apos = False
            paginas = [x for x in range(paginacao.num_pages - (LIMITE_DE_PAGINAS * 2), paginacao.num_pages + 1)]
        else :
            paginacao_apos = True
            if not paginacao_antes:
                paginas += [x for x in range(LIMITE_DE_PAGINAS * 2, LIMITE_DE_PAGINAS * 2 + 2)]
            else:
                paginas += [x for x in range(int(pagina) + 1, int(pagina) + LIMITE_DE_PAGINAS + 1)]
    else:
        paginas = paginacao.page_range    
    return {'paginas': paginas, 'pagina_items': pagina_items, 'paginacao': paginacao, 
               'paginacao_antes': paginacao_antes, 'paginacao_apos': paginacao_apos,
               'pagina': int(pagina)}
     
        
def excluir_foto_ajax(request, caminho_imagem):
    caminho_imagem = caminho_imagem.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    os.unlink(caminho_imagem)
    return HttpResponse("nada")

#View usada pelo Plugin TinyMCE para upload e inserção de foto no texto
def handler_upload_foto(arquivo):
    nome_arquivo = arquivo.name
    diretorio_destino = "%s/img/plugin_tiny_foto/fotos/" % settings.MEDIA_ROOT
    extensao = nome_arquivo[nome_arquivo.rfind("."):]
    nome_arquivo = nome_arquivo[:nome_arquivo.rfind(".")]
    while True:
        if not os.path.exists(diretorio_destino + nome_arquivo + extensao):
            break
        nome_arquivo += "_"
    arquivo_destino = open(diretorio_destino + nome_arquivo + extensao, "wb+")
    for chunk in arquivo.chunks():
        arquivo_destino.write(chunk)
    arquivo_destino.close()  
    return diretorio_destino + nome_arquivo + extensao


#Faz uma requisição ao ceplivre para consutar um cep.    
#def pesquisar_cep_view(request, cep):
    #url = "http://ceplivre.pc2consultoria.com/index.php?module=cep&cep=%s&formato=xml" % cep
    #pagina = urllib2.urlopen(url)
    #dom = minidom.parse(pagina)
    #xml = dom.firstChild
    #ceplivre = xml.childNodes[1]
    #tags = {}
    #for tag in ceplivre.childNodes:
            #if tag.nodeType == tag.ELEMENT_NODE:
                #if tag.firstChild:
                    #tags[tag.tagName] = tag.firstChild.data
    #variaveis = RequestContext(request, tags)
    #return render_to_response("detalhe_cep.html", variaveis)

##Consome o webservice dos correios para calculo de frete
##Codigo de serviços
##41106 - PAC
##40010 - SEDEX
##40215 - SEDEX 10
##40290 - SEDEX HOJE
##81019 - e-SEDEX
##44105 - MALOTE
#def calcular_frete_view(request, servico, origem, destino, peso):
    #url = "http://www.correios.com.br/encomendas/precos/calculo.cfm?resposta=xml&servico=%s&cepOrigem=%s&cepDestino=%s&peso=%s" % (
        #servico, origem, destino, peso)
    #pagina = urllib2.urlopen(url)
    #tags = {}
    #try:
        #dom = minidom.parse(pagina)
        #xml = dom.firstChild        
        #dados_postais = xml.childNodes[3]
        #for tag in dados_postais.childNodes:
            #if tag.nodeType == tag.ELEMENT_NODE:
                #if tag.firstChild:
                    #tags[tag.tagName] = tag.firstChild.data
        #erro = xml.childNodes[5]
        #for tag in erro.childNodes:
            #if tag.nodeType == tag.ELEMENT_NODE:
                #if tag.firstChild:
                    #tags[tag.tagName] = tag.firstChild.data
    #except ExpatError:
        #pass
    #variaveis = RequestContext(request, tags)
    #return render_to_response("calculo_frete.html", variaveis)
