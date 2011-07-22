from pansionat.models import Employer
from pansionat.models import Patient
from pansionat.models import Role
from pansionat.models import Diet
from pansionat.models import Item
from pansionat.models import DietItems
from pansionat.models import MedicalLocation
from pansionat.models import MedicalRole
from pansionat.models import Room
from pansionat.models import BookIt 

from django.contrib import admin

class DietInline(admin.TabularInline):
    model = DietItems
    extra = 10

class DietAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]
    inlines = [DietInline]



admin.site.register(Employer)
admin.site.register(Patient)
admin.site.register(Role)
admin.site.register(Diet, DietAdmin)
admin.site.register(Item)
admin.site.register(MedicalLocation)
admin.site.register(MedicalRole)
admin.site.register(Room)
admin.site.register(BookIt)
