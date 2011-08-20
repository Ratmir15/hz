from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
urlpatterns = patterns('',
    (r'^patients/$', 'pansionat.views.index'),
    (r'^patients/(?P<patient_id>\d+)/$', 'pansionat.views.detail'),
    (r'^rooms/$', 'pansionat.views.rooms'),
    (r'^orders/$', 'pansionat.views.orders'),
    (r'^orders/nakl/(?P<occupied_id>\d+)/$', 'pansionat.views.nakl'),
    (r'^orders/sf/(?P<occupied_id>\d+)/$', 'pansionat.views.schetfactura'),
    (r'^orders/zayava/(?P<occupied_id>\d+)/$', 'pansionat.views.zayava'),
    (r'^orders/pko/(?P<occupied_id>\d+)/$', 'pansionat.views.pko'),
    (r'^reestr/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.reestr'),
    (r'^moves/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.moves'),
    (r'^reports/$', 'pansionat.views.reports'),
    (r'^xt/$', 'pansionat.views.xt'),
    (r'^bookit/$', 'pansionat.views.bookit'),
    (r'^bookit/save/$', 'pansionat.views.bookit_save'),
    (r'^admin/', include(admin.site.urls)),
)
