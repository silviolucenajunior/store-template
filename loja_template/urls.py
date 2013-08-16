from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from development.register import autodiscover_meta, autodiscover_crop
autodiscover_meta()

admin.autodiscover()

autodiscover_crop()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'loja_template.views.home', name='home'),
    # url(r'^loja_template/', include('loja_template.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
