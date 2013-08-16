#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Local

def locais_view(request):
    locais = Local.objects.filter(publicado = True).all()
    variaveis = RequestContext(request, {
        "lojas": locais
    })
    return render_to_response("locais/listagem.html", variaveis)