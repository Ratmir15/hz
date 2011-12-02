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
    (r'^ordersmenu/$', 'pansionat.views.ordersmenu'),
    (r'^orders/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.orders_by_month'),
    (r'^filterorders/$', 'pansionat.views.filterorders'),
    (r'^orders/$', 'pansionat.views.orders'),
    (r'^import/$', 'pansionat.orders.import_orders'),
    (r'^importfile/$', 'pansionat.orders.import_file'),
    (r'^test/$', 'pansionat.orders.test_orders'),
    (r'^testfile/$', 'pansionat.orders.testfile'),
    (r'^importdiet/$', 'pansionat.orders.importdiet'),
    (r'^books/$', 'pansionat.views.books'),
    (r'^mpp/$', 'pansionat.proc.mpp'),
    (r'^mpp/save/$', 'pansionat.proc.mpp_save'),
    (r'^mpp/new/$', 'pansionat.proc.mpp_new'),
    (r'^mpp/(?P<mpt_id>\d+)/$', 'pansionat.proc.mpp_edit'),
    (r'^mpp/(?P<mpt_id>\d+)/new$', 'pansionat.proc.mpp_new_price'),
    (r'^mpp/(?P<mpt_id>\d+)/saveprice', 'pansionat.proc.mpp_save_price'),
    (r'^mpp/delete/(?P<mptp_id>\d+)', 'pansionat.proc.mpp_delete_price'),
    (r'^orders/patient/(?P<patient_id>\d+)/$', 'pansionat.views.orders_patient'),
    (r'^orders/nakl/(?P<occupied_id>\d+)/$', 'pansionat.views.nakl'),
    (r'^diet/(?P<order_id>\d+)/$', 'pansionat.views.orderdiet'),
    (r'^diet/save/$', 'pansionat.views.orderdiet_save'),
    (r'^mp/(?P<order_id>\d+)/(?P<mp_type_order>\d+)/$', 'pansionat.views.medical_procedures_schedule'),
    (r'^mp/(?P<order_id>\d+)/$', 'pansionat.views.medical_procedures'),
    (r'^mp/(?P<order_id>\d+)/print/$', 'pansionat.views.medical_procedures_print'),
#    (r'^mp/print/(?P<mp_type_id>\d+)/(?P<year>\d+)\.(?P<month>\d+)\.(?P<day>\d+)/$', 'pansionat.views.schedule_print'),
    (r'^mp/print/$', 'pansionat.views.schedule_print'),
    (r'^mp/save/$', 'pansionat.views.mp_save'),
    (r'^mps/save/$', 'pansionat.views.medical_procedures_schedule_save'),
    (r'^ih/(?P<order_id>\d+)/$', 'pansionat.views.ill_history_head'),
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
    (r'^delbook/(?P<roombook_id>\d+)/$', 'pansionat.views.delbook'),
    (r'^order/delete/(?P<order_id>\d+)/$', 'pansionat.views.delorder'),
    (r'^order/(?P<order_id>\d+)/$', 'pansionat.orders.order_edit'),
    (r'^order/json/(?P<order_id>\d+)/$', 'pansionat.orders.order_json'),
    (r'^order/save/$', 'pansionat.orders.order_save'),
    (r'^reestr/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.reestr'),
    (r'^moves/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.moves'),
    (r'^mov/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.mov'),
    (r'^movinfo/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.movinfo'),
    (r'^movanal/(?P<year>\d+)/(?P<month>\d+)/$', 'pansionat.views.movanal'),
    (r'^mov/(?P<year>\d+)/(?P<month>\d+)/(?P<tp>\d+)/$', 'pansionat.views.movtp'),
    (r'^reports/$', 'pansionat.reports.reports'),
    (r'^report/(?P<tp>\d+)/$', 'pansionat.reports.report'),
    (r'^processreport/(?P<tp>\d+)/$', 'pansionat.reports.processreport'),
    (r'^xt/$', 'pansionat.views.xt'),
    (r'^bookit/$', 'pansionat.views.bookit'),
    (r'^net/$', 'pansionat.orders.net'),
    (r'^zreport/$', 'pansionat.reports.zreport'),
    (r'^zprint/$', 'pansionat.reports.zprint'),
    (r'^mpreport/$', 'pansionat.views.mpreport'),
    (r'^dietday/$', 'pansionat.views.dietday'),
    (r'^dietday/choose/$', 'pansionat.views.dietdaychoose'),
    (r'^dietday/report/$', 'pansionat.views.dietdayreport'),
    (r'^diets/$', 'pansionat.views.diets'),
    (r'^diets/print/$', 'pansionat.views.diets_print'),
    (r'^book/handler/$', 'pansionat.views.book_handler'),
    (r'^order/$', 'pansionat.views.order'),
    (r'^init/$', 'pansionat.views.init'),
    (r'^clear/$', 'pansionat.views.clear'),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'pansionat.views.index'),
)
