from django.db import models

# Create your models here.
class Employer(models.Model):
	family = models.CharField(max_length=50)
	name = models.CharField(max_length=50)
	sname = models.CharField(max_length=50)

class Patient(models.Model):
    family = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    sname = models.CharField(max_length=50)
    birth_date = models.DateField()
    grade = models.CharField(max_length=50)
    passport_number = models.CharField(max_length=20)
    passport_whom = models.CharField(max_length=30)
    address = models.CharField(max_length=200)
    def __unicode__(self):
        return self.family+' '+self.name+' '+self.sname

#    birth_date = models.DateField()
#    grade = models.CharField(max_length = 30)

class Role(models.Model):
	name = models.CharField(max_length=50)
	
class EmployerRoleHistory(models.Model):
	employer = models.ForeignKey(Employer)
	role = models.ForeignKey(Role)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class Diet(models.Model):
	name = models.CharField(max_length=50)
	
class Item(models.Model):
	name = models.CharField(max_length=50)

class ItemPrices(models.Model):
	item = models.ForeignKey(Item)
	price = models.DecimalField(decimal_places=2,max_digits=8)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')
	
class DietItems(models.Model):
	diet = models.ForeignKey(Diet)
	item = models.ForeignKey(Item)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class MedicalLocation(models.Model):
	name = models.CharField(max_length=50)

class MedicalRole(models.Model):
	name = models.CharField(max_length=50)

class MedicalLocationRoles(models.Model):
	location = models.ForeignKey(MedicalLocation)
	role = models.ForeignKey(MedicalRole)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class Busy(models.Model):
	location = models.ForeignKey(MedicalLocation)
	employer = models.ForeignKey(Employer)
	patient = models.ForeignKey(Patient)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class Customer(models.Model):
    name = models.CharField(max_length = 50)
    is_show = models.BooleanField()

class Order(models.Model):
    code = models.CharField(max_length = 10)
    patient = models.ForeignKey(Patient)
    customer = models.ForeignKey(Customer)
    directive = models.ForeignKey(Customer, related_name='dir')
    start_date = models.DateField('date started')
    end_date = models.DateField('date finished')
    price = models.DecimalField(decimal_places = 2,max_digits=8)
    is_with_child = models.BooleanField()


# Room book service
#ROOM_TYPE = (
#    ("L", "Lux"),
#    ("D", "Default"),
#)
    
class RoomType(models.Model):
    name = models.CharField(max_length = 50)
    places = models.IntegerField()
    price = models.DecimalField(decimal_places=2,max_digits=8)
    is_additional_people_available = models.BooleanField()
    is_blocked_for_single = models.BooleanField()


class Room (models.Model):
    name = models.CharField(max_length = 50) # it can be room number or name of room
    room_type = models.ForeignKey(RoomType)
    description = models.CharField(max_length = 65535)

class Occupied(models.Model):
    order = models.ForeignKey(Order)
    room = models.ForeignKey(Room)
    start_date = models.DateTimeField("Start book date")
    end_date = models.DateTimeField("End book date")
    description = models.CharField(max_length = 65535)

class Book(models.Model):
    start_date = models.DateTimeField("Start book date")
    end_date = models.DateTimeField("End book date")
    name = models.CharField(max_length = 65535)
    phone = models.CharField(max_length = 11)
    description = models.CharField(max_length = 65535)

class RoomBook(models.Model):
    room = models.ForeignKey(Room)
    book = models.ForeignKey(Book)

class TypeBook(models.Model):
    room_type = models.ForeignKey(RoomType)
    amount = models.IntegerField()
    book = models.ForeignKey(Book)
