from pansionat.models import Employer
from pansionat.models import Patient
from pansionat.models import Role
from pansionat.models import EmployerRoleHistory
from pansionat.models import Diet
from pansionat.models import Item
from pansionat.models import DietItems
from pansionat.models import MedicalLocation
from pansionat.models import MedicalRole
from pansionat.models import Room
from pansionat.models import RoomType 
from pansionat.models import Occupied
from pansionat.models import Book
from pansionat.models import RoomBook
from pansionat.models import TypeBook
from pansionat.models import Order 
from pansionat.models import Customer 
from pansionat.models import OrderType

from django.contrib import admin
from mysite.pansionat.models import Order, Customer, IllHistoryFieldValue, IllHistoryFieldType, MedicalProcedureType, RoomPlace

class DietInline(admin.TabularInline):
    model = DietItems
    extra = 10

class DietAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
    ]
    inlines = [DietInline]

class RoomAdmin(admin.ModelAdmin):
    list_display = ['name','room_place','disabled']


admin.site.register(Employer)
admin.site.register(EmployerRoleHistory)
admin.site.register(Patient)
admin.site.register(Role)
admin.site.register(Diet, DietAdmin)
admin.site.register(Item)
admin.site.register(MedicalLocation)
admin.site.register(MedicalRole)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomType)
admin.site.register(Occupied)
admin.site.register(Book)
admin.site.register(RoomBook)
admin.site.register(RoomPlace)
admin.site.register(TypeBook)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(IllHistoryFieldType)
admin.site.register(MedicalProcedureType)
admin.site.register(OrderType)