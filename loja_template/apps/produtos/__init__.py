#-*-  coding: utf-8 -*-

from django.db.models import get_models, get_app, get_model
from development.imagem import gerador_criar_miniaturas

app = get_app(__name__.split(".")[-1])
models = get_models(app)

for model in models:
    gerador_criar_miniaturas(model)
