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
	
