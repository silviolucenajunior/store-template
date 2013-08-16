#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

#plugin tiny_mce
urlpatterns = patterns("galerias.views",
    (r'^cadastrar-foto-plugin/$', 'cadastrar_foto_plugin_view'),
    (r'^cadastrar-foto-plugin-ajax/$', 'cadastrar_foto_plugin_ajax'),
)

urlpatterns += patterns("galerias.views",
    (r'^adicionar_foto_galeria/(?P<id_foto>.*)/(?P<id_galeria>.*)/$', 'adicionar_foto_galeria_ajax'),
    (r'^cadastrar_galeria/$', 'cadastrar_galeria'),
    (r'^cropar_foto/(?P<foto>.*)/$', 'manipular_foto_view'),
    (r'^deletar_foto/(?P<id_foto>.*)/$', 'deletar_foto_ajax'),
    (r'^fotos_json/$', 'fotos_json'),
    (r'^gerenciar/$', 'gerenciador_view'),
    (r'^listar_galerias/$', 'listar_galerias_view'),
    (r'^manipular_foto/redimensionar/(?P<foto>.*)/$', 'redimensionar_foto_view'),
    (r'^manipular_foto/(?P<foto>.*)/$', 'manipular_foto_view'),
    (r'^visualizar_galeria/categoria/(?P<categoria_slug>.*)/(?P<autor_username>.*)/$', 'visualizar_galerias_por_categoria_autor_view'),
    (r'^visualizar_galeria/categoria/(?P<categoria_slug>.*)/$', 'visualizar_galerias_por_categoria_view'),
    (r'^visualizar_galeria/(?P<galeria_id>.*)/$', 'visualizar_galeria_view'),
    (r'^visualizar_galeria/autor/(?P<autor_username>.*)/$', 'visualizar_galerias_por_autor_view'),
    (r'^previa_galeria/(?P<galeria_id>.*)/$', 'visualizar_galeria_previa_view'),
    (r'^setar_ordem_foto/(?P<id_foto>.*)/(?P<nova_ordem>.*)/$', 'setar_ordem_foto_ajax'),
    (r'^upload_progress/$', 'upload_progress')
)