# ACTION_CHECKBOX_NAME is unused, but should stay since its import from here
# has been referenced in documentation.
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.options import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin.options import StackedInline, TabularInline
from django.contrib.admin.sites import AdminSite, site
from django.contrib.admin.filters import (ListFilter, SimpleListFilter,
                                          FieldListFilter, BooleanFieldListFilter, RelatedFieldListFilter,
                                          ChoicesFieldListFilter, DateFieldListFilter, AllValuesFieldListFilter)


def autodiscover_meta():
    """
Auto-discover INSTALLED_APPS admin.py modules and fail silently when
not present. This forces an import on them to register any admin bits they
may want.
"""

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    from django.db.models import get_models, get_app, get_model
    from development.imagem import gerador_criar_miniaturas, gerador_crop_admin




    for app in settings.INSTALLED_APPS:
        print app
        print "#######################################"
        modulo = get_app(app.split(".")[-1])
        models = get_models(modulo)

        for model in models:
            gerador_criar_miniaturas(model)

def autodiscover_crop():
    """
Auto-discover INSTALLED_APPS admin.py modules and fail silently when
not present. This forces an import on them to register any admin bits they
may want.
"""

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule
    from django.db.models import get_models, get_app, get_model
    from development.imagem import gerador_criar_miniaturas, gerador_crop_admin



    for app in settings.INSTALLED_APPS:
        print app
        print "#######################################"
        modulo = get_app(app.split(".")[-1])
        models = get_models(modulo)

        for model in models:
            gerador_crop_admin(model)
