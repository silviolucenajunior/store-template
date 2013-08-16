#-*- coding: utf-8 -*-
def publicar_action(modeladmin, request, queryset):
    if request.user.is_superuser:
        linhas_atualizadas = queryset.update(publicado = True)
    else:    
        linhas_atualizadas = queryset.filter(autor = request.user).update(publicado = True)
    if linhas_atualizadas == 1:
        mensagem = "1 %s publicada com sucesso." % modeladmin.model._meta.verbose_name_plural
    else:
        mensagem = "%s %s publicadas com sucesso." % (linhas_atualizadas, modeladmin.model._meta.verbose_name_plural)
    modeladmin.message_user(request, mensagem)

def despublicar_action(modeladmin, request, queryset):
    if request.user.is_superuser:
        linhas_atualizadas = queryset.update(publicado = False)
    else:    
        linhas_atualizadas = queryset.filter(autor = request.user).update(publicado = True)
    if linhas_atualizadas == 1:
        mensagem = "1 %s despublicada com sucesso." % modeladmin.model._meta.verbose_name_plural
    else:
        mensagem = "%s %s despublicadas com sucesso." % (linhas_atualizadas, modeladmin.model._meta.verbose_name_plural)
    modeladmin.message_user(request, mensagem)
    