#-*- coding:utf-8 -*-
import os
from django.db.models import signals

from django.contrib import admin
from django.contrib.admin import site

def post_delete(signal, instance, sender, **kwargs):
    instance.deletar_miniaturas()

def gerador_criar_miniaturas(classe_alvo, self = None):
    from utilidades.imagem import criar_miniatura
    if hasattr(classe_alvo, "__miniatura_admin__"):
        miniatura_admin = getattr("__miniatura_admin__")
    else:
        miniatura_admin = (32, 32)
    campos_processados = []
    if hasattr(classe_alvo, "__miniaturas__"):
    #Adiciona o metodo para gerar as miniaturas
        def gerar_miniaturas(self):
            campos_processados = []
            for miniatura in getattr(self, "__miniaturas__"):
                if hasattr(self, miniatura[0]):
                    campo = self.__getattribute__(miniatura[0])
                    if campo:
                        diretorio, imagem = os.path.split(campo.path)
                        if not os.path.exists("%s/thumbnails" % diretorio):
                            os.mkdir("%s/thumbnails" % diretorio)
                        caminho_thumbnail = "%s/thumbnails/%s_%s_%s" % (diretorio, miniatura[1][0], miniatura[0],imagem)
                        criar_miniatura(campo.path, (miniatura[1][1], miniatura[1][2]), caminho_thumbnail, True)

                        if not campo in campos_processados:
                            campos_processados.append(campo)
                            caminho_thumbnail = "%s/thumbnails/admin_%s_%s" % (diretorio, miniatura[0], imagem)
                            criar_miniatura(campo.path, miniatura_admin, caminho_thumbnail, True)
        setattr(classe_alvo, "criar_miniaturas", gerar_miniaturas)

        #Adiciona os metodos para recuperar as miniaturas
        campos_processados = []
        for miniatura in getattr(classe_alvo, "__miniaturas__"):
            if classe_alvo.__dict__.has_key(miniatura[0]):
                def thumbnail_factory(linha_miniatura):
                    def thumbnail(self):
                        campo = self.__getattribute__(linha_miniatura[0])
                        if campo:
                            diretorio, imagem = os.path.split(campo.url)
                            return "%s/thumbnails/%s_%s_%s" % (diretorio, linha_miniatura[1][0], linha_miniatura[0],  imagem)
                        else:
                            return ""
                    return thumbnail
                funcao_thumbnail = thumbnail_factory(miniatura)
                setattr(classe_alvo, "%s_%s_thumbnail" % (miniatura[0], miniatura[1][0]), funcao_thumbnail)

                if not miniatura[0] in campos_processados:
                    campos_processados.append(miniatura[0])

                    def admin_thumbnail_factory(linha_miniatura):
                        def admin_thumbnail(self) :
                            campo = self.__getattribute__(linha_miniatura[0])
                            if campo:
                                valor = True
                            else:
                                valor = False
                            if campo:
                                diretorio, imagem = os.path.split(campo.url)
                                return u'<a href="%s/%s" class="fancy-trigger"><img src="%s/thumbnails/admin_%s_%s"/></a>' % (
                                    diretorio, imagem, diretorio, linha_miniatura[0], imagem)
                            else:
                                return ""
                        return admin_thumbnail
                    funcao_thumbnail = admin_thumbnail_factory(miniatura)
                    funcao_thumbnail.short_description = '%s' % miniatura[0]
                    funcao_thumbnail.allow_tags = True
                    setattr(classe_alvo, "admin_%s_thumbnail" % miniatura[0], funcao_thumbnail)


        def deletar_miniaturas(self):
            try:
                campos_processados = []
                for miniatura in getattr(classe_alvo, "__miniaturas__"):
                    campo = self.__getattribute__(miniatura[0])
                    diretorio, imagem = os.path.split(campo.path)
                    thumbnail_file = "%s/thumbnails/%s_%s_%s" % (diretorio, miniatura[1][0], miniatura[0], imagem)
                    os.unlink(thumbnail_file)
                    if not miniatura[0] in campos_processados:
                        campos_processados.append(miniatura[0])
                        thumbnail_file = "%s/thumbnails/admin_%s_%s" % (diretorio, miniatura[0], imagem)
                        os.unlink(thumbnail_file)

            except Exception:
                pass
        setattr(classe_alvo, "deletar_miniaturas", deletar_miniaturas)

        signals.pre_delete.connect(post_delete, sender = classe_alvo)

def gerador_crop_admin(classe_alvo):
    if hasattr(classe_alvo, "__crop__"):
        crop = getattr(classe_alvo, "__crop__")
        classe_admin = site._registry[classe_alvo].__class__
        from utilidades.imagem import cropar_imagem_view
        print classe_admin
        print "-------------------"
        class CropAdmin(classe_admin):
            def response_add(self, request, obj, post_url_continue = "../%s/") :
                redirect = super(CropAdmin, self).response_add(request, obj)
                obj.criar_miniaturas()
                request.session['obj_crop'] = obj
                redirect = redirect.__getitem__("Location")
                return cropar_imagem_view(request, obj.imagem.name, redirect, crop["largura"], crop["altura"], crop["proporcao"], POST_DATA = True, manter_original = crop["manter_original"])#

            def response_change(self, request, obj):
                redirect = super(CropAdmin, self).response_change(request, obj)
                if request.FILES.has_key('imagem'):
                    redirect = redirect.__getitem__("Location")
                    request.session['obj_crop'] = obj
                    return cropar_imagem_view(request, obj.imagem.name, redirect, crop["largura"], crop["altura"], crop["proporcao"], POST_DATA = True, manter_original = crop["manter_original"])
                else:
                    return redirect
        site.unregister(classe_alvo)
        site.register(classe_alvo, CropAdmin)






