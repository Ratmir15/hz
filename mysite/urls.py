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
    (r'^patients/$', 'pansionat.views.patients'),
    (r'^accounts/login/$', 'pansionat.views.index'),
    (r'^forbidden/$', 'pansionat.views.forbidden'),
    (r'^login/$', 'pansionat.views.my_view'),
    (r'^logout/$', 'pansionat.views.logout_page'),
    (r'^patients/(?P<patient_id>\d+)/$', 'pansionat.views.patient_edit'),
    (r'^patients/new/$', 'pansionat.views.patient_new'),
    (r'^patients/save/$', 'pansionat.views.patient_save'),
    (r'^clients/$', 'pansionat.views.clients'),
    (r'^clients/(?P<client_id>\d+)/$', 'pansionat.views.client_edit'),
    (r'^clients/new/$', 'pansionat.views.client_new'),
    (r'^clients/save/$', 'pansionat.views.client_save'),
    (r'^rooms/$', 'pansionat.views.rooms'),
    (r'^orders/$', 'pansionat.views.orders'),
    (r'^orders/patient/(?P<patient_id>\d+)/$', 'pansionat.views.orders_patient'),
    (r'^orders/nakl/(?P<occupied_id>\d+)/$', 'pansionat.views.nakl'),
    (r'^illhistory/(?P<order_id>\d+)/$', 'pansionat.views.ill_history_edit'),
    (r'^illhistory/records/(?P<order_id>\d+)/$', 'pansionat.views.records'),
    (r'^illhistory/record/(?P<object_id>\d+)/$', 'pansionat.views.record_edit'),
    (r'^illhistory/record/new/(?P<ill_history_id>\d+)/$', 'pansionat.views.record_new'),
    (r'^illhistory/record/save/$', 'pansionat.views.record_save'),
    (r'^illhistory/print/(?P<order_id>\d+)/$', 'pansionat.views.ill_history'),
    (r'^illhistory/save/$', 'pansionat.views.ill_history_save'),
    (r'^orders/rootik/(?P<order_id>\d+)/$', 'pansionat.views.rootik'),
    (r'^orders/sf/(?P<occupied_id>\d+)/$', 'pansionat.views.schetfactura'),
    (r'^orders/zayava/(?P<occupied_id>\d+)/$', 'pansionat.views.zayava'),
    (r'^orders/pko/(?P<occupied_id>\d+)/$', 'pansionat.views.pko'),
    (r'^reestr/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.reestr'),
    (r'^moves/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.moves'),
    (r'^reports/$', 'pansionat.views.reports'),
    (r'^xt/$', 'pansionat.views.xt'),
    (r'^bookit/$', 'pansionat.views.bookit'),
    (r'^book/handler/$', 'pansionat.views.book_handler'),
    (r'^order/$', 'pansionat.views.order'),
    (r'^init/$', 'pansionat.views.init'),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'pansionat.views.index'),
)
