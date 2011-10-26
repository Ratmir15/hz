# coding: utf-8
from django.db import models

# Create your models here.
class Employer(models.Model):
    family = models.CharField(max_length=50, verbose_name = 'Фамилия')
    name = models.CharField(max_length=50, verbose_name = 'Имя')
    sname = models.CharField(max_length=50, verbose_name = 'Отчество')
    def __unicode__(self):
        return self.family+' '+self.name+' '+self.sname

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


MARRIAGE = (
    ("M","женат/замужем"),
    ("H","холост(а)"),
    ("D","разведен(а)"),
)

class Patient(models.Model):
    family = models.CharField(max_length=50, verbose_name = 'Фамилия')
    name = models.CharField(max_length=50, verbose_name = 'Имя')
    sname = models.CharField(max_length=50, verbose_name = 'Отчество', blank=True)
    birth_date = models.DateField(verbose_name = 'Дата рождения', blank=True, null=True)
    grade = models.CharField(max_length=50, verbose_name = 'Должность', blank=True, null=True)
    profession = models.CharField(max_length=50, verbose_name = 'Профессия', blank=True, null=True)
    marriage = models.CharField(max_length = 1, choices = MARRIAGE, verbose_name='Семейное положение', blank=True, null=True)
    passport_number = models.CharField(unique = True, max_length=20,\
                    verbose_name = 'Серия и номер паспорта')
    passport_whom = models.CharField(max_length=100, verbose_name = 'Кем выдан паспорт', blank=True)
    address = models.CharField(max_length=200, verbose_name = 'Адрес', blank=True, null=True)
    def fio(self):
        return self.family+' '+self.name+' '+self.sname
    def __unicode__(self):
        return self.family+' '+self.name+' '+self.sname

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

#    birth_date = models.DateField()
#    grade = models.CharField(max_length = 30)

class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name = 'Название')
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

class EmployerRoleHistory(models.Model):
    employer = models.ForeignKey(Employer, verbose_name = 'Сотрудник')
    role = models.ForeignKey(Role, verbose_name = 'Должность')
    start_date = models.DateField('Дата назначения')
    end_date = models.DateField('Дата увольнения')
    def __unicode__(self):
        return self.employer.__unicode__()+'/'+self.role.__unicode__()

    class Meta:
        verbose_name = 'История должностей'
        verbose_name_plural = 'История должностей'

class Diet(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Диета'
        verbose_name_plural = 'Диеты'

class Item(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

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

    class Meta:
        verbose_name = 'Кабинет'
        verbose_name_plural = 'Кабинеты'

class MedicalRole(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

class MedicalLocationRoles(models.Model):
	location = models.ForeignKey(MedicalLocation)
	role = models.ForeignKey(MedicalRole)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class MedicalProcedureType(models.Model):
    name = models.CharField(max_length = 50)
    order = models.IntegerField()
    capacity = models.IntegerField()
    duration = models.IntegerField()
    start_time = models.TimeField()
    finish_time = models.TimeField()
    optional = models.CharField(max_length=100)
    def optional_values(self):
        return self.optional.split(',')
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип медицинской процедуры'
        verbose_name_plural = 'Типы медицинской процедуры'

class Busy(models.Model):
	location = models.ForeignKey(MedicalLocation)
	employer = models.ForeignKey(Employer)
	patient = models.ForeignKey(Patient)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')

class Customer(models.Model):
    name = models.CharField(max_length = 50, verbose_name = 'Название')
    shortname = models.CharField(max_length = 50, verbose_name = 'Короткое название')
    inn = models.CharField(null = True, blank=True, max_length=20, verbose_name='ИНН')
    bank = models.CharField(max_length=40, blank=True, verbose_name='Банк')
    rs = models.CharField(max_length=50, blank=True, verbose_name='Расчетный счет')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    is_show = models.BooleanField(verbose_name = 'Показывать в отчетах')
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class RoomType(models.Model):
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 100)
    places = models.IntegerField()
    price = models.DecimalField(decimal_places=2,max_digits=8)
    price_alone = models.DecimalField(decimal_places=2,max_digits=8)
    is_additional_people_available = models.BooleanField()
    is_blocked_for_single = models.BooleanField()
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип номеров'
        verbose_name_plural = 'Типы номеров'


class Room (models.Model):
    name = models.CharField(max_length = 50) # it can be room number or name of room
    room_type = models.ForeignKey(RoomType)
    description = models.CharField(max_length = 10000)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

class Order(models.Model):
    code = models.CharField(max_length = 10, verbose_name = 'Номер заказа')
    putevka = models.CharField(max_length = 6, verbose_name = 'Номер путевки')
    patient = models.ForeignKey(Patient)
    customer = models.ForeignKey(Customer, verbose_name = 'Предприятие', blank=True)
    room = models.ForeignKey(Room)
    directive = models.ForeignKey(Customer, related_name='dir', verbose_name = 'Оплачивающий', blank= True)
    start_date = models.DateField('Дата заезда')
    end_date = models.DateField('Даты выезда')
    price = models.DecimalField(decimal_places = 2,max_digits=8, verbose_name = 'Стоимость')
    is_with_child = models.BooleanField(verbose_name = 'Мать и дитя')
    payd_by_patient = models.BooleanField(verbose_name = 'Оплачивается пациентом')
    reab = models.BooleanField(verbose_name = 'Реабилитация')
    def __unicode__(self):
        return self.code
    def start_date_n(self):
        return self.start_date.strftime('%Y.%m.%d')
    def end_date_n(self):
        return self.end_date.strftime('%Y.%m.%d')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
#        permissions = (
#            ("arm_registration", "REGISTRATION"))

class OrderDiet(models.Model):
    diet = models.ForeignKey(Diet)
    order = models.ForeignKey(Order)

    class Meta:
        verbose_name = 'Выбор диеты'
        verbose_name_plural = 'Выбор диеты'

class OrderMedicalProcedure(models.Model):
    order = models.ForeignKey(Order)
    mp_type = models.ForeignKey(MedicalProcedureType)
    times = models.IntegerField()
    add_info = models.CharField(max_length=50)

class OrderMedicalProcedureSchedule(models.Model):
    order = models.ForeignKey(Order)
    mp_type = models.ForeignKey(MedicalProcedureType)
    p_date = models.DateField()
    slot = models.IntegerField()

class IllHistoryFieldTypeGroup(models.Model):
    description = models.CharField(max_length=100, verbose_name='Заголовок')
    order = models.IntegerField()
    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'Группа полей истории болезни'
        verbose_name_plural = 'Группы полей истории болезни'

class IllHistoryFieldType(models.Model):
    description = models.CharField(max_length=100, verbose_name='Описание')
    lines = models.IntegerField()
    defval = models.CharField(max_length=255)
    order = models.IntegerField()
    group = models.ForeignKey(IllHistoryFieldTypeGroup)
    def default_values(self):
        return self.defval.split(',')
    def height(self):
        return self.lines*20
    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'Тип поля истории болезни'
        verbose_name_plural = 'Типы полей истории болезни'

class IllHistory(models.Model):
    order = models.OneToOneField(Order, verbose_name='Путевка')
#    first_diagnose = models.CharField(max_length=255, blank=True, verbose_name='Диагноз поступления')
#    main_diagnose = models.CharField(max_length=255, blank=True, verbose_name='Основной диагноз')
#    secondary_diagnose = models.CharField(max_length=255, blank=True, verbose_name='Сопутствующий диагноз')
#    conditions = models.CharField(max_length=255, blank=True, verbose_name='Условия труда')
#    complaints = models.CharField(max_length=255, blank=True, verbose_name='Жалобы больного')
#    general = models.CharField(max_length=255, blank=True, verbose_name='Общий анализ')
#    beginning = models.CharField(max_length=255,blank=True, verbose_name='Начало и развитие настоящего заболевания')
#    state = models.CharField(max_length=255,blank=True, verbose_name='Состояние удовлетворительное')
#    body = models.CharField(max_length=255,blank=True, verbose_name='Телосложение: правильное, неправильное')
#    astenik = models.CharField(max_length=100,blank=True, verbose_name='Астеник, нормастеник, гиперстеник')
#    state = models.CharField(max_length=255,blank=True, verbose_name='Состояние удовлетворительное')
#    state = models.CharField(max_length=255,blank=True, verbose_name='Состояние удовлетворительное')
#    state = models.CharField(max_length=255,blank=True, verbose_name='Состояние удовлетворительное')

    class Meta:
        verbose_name = 'История болезни'
        verbose_name_plural = 'Истории болезни'

class IllHistoryFieldValue(models.Model):
    ill_history = models.ForeignKey(IllHistory, verbose_name='История болезни')
    ill_history_field = models.ForeignKey(IllHistoryFieldType, verbose_name='Поле')
    value = models.CharField(max_length=255, verbose_name='Значение поля')

    class Meta:
        verbose_name = 'Значение поля'
        verbose_name_plural = 'Значения полей'


class IllHistoryRecord(models.Model):
    ill_history = models.ForeignKey(IllHistory, verbose_name='История болезни')
    datetime = models.DateTimeField(verbose_name='Дата записи')
    text = models.CharField(max_length=1000, verbose_name='Текст')

    class Meta:
        verbose_name = 'Запись истории болезни'
        verbose_name_plural = 'Записи историй болезни'

# Room book service
#ROOM_TYPE = (
#    ("L", "Lux"),
#    ("D", "Default"),
#)

class Occupied(models.Model):
    order = models.ForeignKey(Order)
    room = models.ForeignKey(Room)
    start_date = models.DateField("Start book date")
    end_date = models.DateField("End book date")
    description = models.CharField(max_length = 10000)
    def __unicode__(self):
        return self.order.code

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'

class Book(models.Model):
    start_date = models.DateTimeField("Start book date")
    end_date = models.DateTimeField("End book date")
    name = models.CharField(max_length = 10000)
    phone = models.CharField(max_length = 100)
    description = models.CharField(max_length = 10000)
    def start_date_n(self):
        return self.start_date.strftime('%Y.%m.%d')
    def end_date_n(self):
        return self.end_date.strftime('%Y.%m.%d')

class OrderDay(models.Model):
    room = models.ForeignKey(Room, verbose_name = 'Комната')
    busydate = models.DateField(verbose_name = 'Дата')
    order = models.ForeignKey(Order, verbose_name = 'Заказ', null=True)
    book = models.ForeignKey(Book, verbose_name = 'Бронь', null=True)
    is_with_child = models.BooleanField(verbose_name = 'Мать и дитя')
    def busydate_n(self):
        return self.busydate.strftime('%Y.%m.%d')

    class Meta:
        verbose_name = 'День заказа'
        verbose_name_plural = 'Дни заказов'

class RoomBook(models.Model):
    room = models.ForeignKey(Room)
    book = models.ForeignKey(Book)

class TypeBook(models.Model):
    room_type = models.ForeignKey(RoomType)
    amount = models.IntegerField()
    book = models.ForeignKey(Book)
