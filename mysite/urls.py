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
    (r'^orders/$', 'pansionat.views.orders'),
    (r'^test/(?P<test_id>\d+)/$', 'pansionat.views.test'),
    (r'^orders/nakl/(?P<order_id>\d+)/$', 'pansionat.views.nakl'),
    (r'^xt/$', 'pansionat.views.xt'),
    (r'^bookit/$', 'pansionat.views.bookit'),
    (r'^admin/', include(admin.site.urls)),
)
