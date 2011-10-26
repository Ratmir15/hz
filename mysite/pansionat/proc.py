# coding: utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.forms.models import ModelForm
from django.shortcuts import render_to_response, redirect
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import MedicalProcedureType, MedicalProcedureTypePrice

__author__ = 'rpanov'

@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp(request):
    list = MedicalProcedureType.objects.all().order_by("name")
    values = {"occupied_list":list}
    return render_to_response('pansionat/mplist.html', MenuRequestContext(request, values))

class MedicalProcedureTypeForm(ModelForm):
    class Meta:
        model = MedicalProcedureType
    def clean_family(self):
        data = self.cleaned_data['family']
        data = data.strip().capitalize()
        return data

class MedicalProcedureTypePriceForm(ModelForm):
    class Meta:
        model = MedicalProcedureTypePrice
        exclude = ('mpt')

@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp_new(request):
    form = MedicalProcedureTypeForm()
    values = {'form' : form, "prices":[]}
    return render_to_response('pansionat/mpte.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp_new_price(request, mpt_id):
    form = MedicalProcedureTypePriceForm()
    values = {'form' : form, "mpt_id":mpt_id}
    return render_to_response('pansionat/mp_price.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp_save_price(request, mpt_id):
    if request.method == 'POST':
        form = MedicalProcedureTypePriceForm(request.POST)

        if form.is_valid():
            mptp = form.save(commit = False)
            mptp.mpt = MedicalProcedureType.objects.get(id = mpt_id)
            mptp.save()
            return redirect('/mpp/'+str(mpt_id))
        else:
            values = {'form' : form, "mpt_id":mpt_id}
            return render_to_response('pansionat/mp_price.html', MenuRequestContext(request, values))
    return mpp_new_price(request, mpt_id)

@login_required
def mpp_delete_price(request, mptp_id):
    obj = MedicalProcedureTypePrice.objects.get(id=mptp_id)
    mpt_id = obj.mpt_id
    obj.delete()
    return redirect('/mpp/'+str(mpt_id))


@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp_edit(request, mpt_id):
    mpt = MedicalProcedureType.objects.get(id=mpt_id)
    form = MedicalProcedureTypeForm(instance=mpt)
    prices = mpt.medicalproceduretypeprice_set.order_by("add_info","-date_applied")
    values = {"prices":prices,"instance_id":mpt.id,"form":form}
    return render_to_response('pansionat/mpte.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_medicalproceduretypeprice', login_url='/forbidden/')
def mpp_save(request):
    if request.method == 'POST':
        id = request.POST.get('instance_id')
        if id is None:
            form = MedicalProcedureTypeForm(request.POST)
            prices = []
        else:
            instance = MedicalProcedureType.objects.get(id = id)
            form = MedicalProcedureTypeForm(request.POST, instance = instance)
            prices = instance.medicalproceduretypeprice_set.order_by("add_info","-date_applied")

        if form.is_valid():
            instance = form.save()
            form = MedicalProcedureTypeForm(instance = instance)
            values = {'form' : form, "prices":prices, 'instance_id' : instance.id}
        else:
            values = {'form' : form, 'instance_id' : id}
        return render_to_response('pansionat/mpte.html', MenuRequestContext(request, values))
    return mpp_new(request)

class MedicalPriceReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        list = MedicalProcedureType.objects.all().order_by("name")
        d = []
        for obj in list:
            d.append({'FIO':obj.name, 'ROOM':obj.actual_price()})
        z = {'REPORTDATE': str(cleaned_report_date)}
        return z,d


