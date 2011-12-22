# coding: utf-8
import datetime
from django.db import models, connection

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
    passport_number = models.CharField(max_length=20,\
                    verbose_name = 'Серия и номер паспорта')
    passport_whom = models.CharField(max_length=100, verbose_name = 'Кем выдан паспорт', blank=True)
    address = models.CharField(max_length=200, verbose_name = 'Адрес', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон',blank=True,null=True)
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
    weight = models.DecimalField(decimal_places=3,max_digits=7)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class Piece(models.Model):
    name = models.CharField(max_length = 50)

    class Meta:
        verbose_name = 'Часть блюда'
        verbose_name_plural = 'Части блюд'
        
class ItemPiece(models.Model):
    item = models.ForeignKey(Item)
    piece = models.ForeignKey(Piece)
    weight = models.DecimalField(decimal_places=3,max_digits=7)

class ItemPrices(models.Model):
	item = models.ForeignKey(Item)
	price = models.DecimalField(decimal_places=2,max_digits=8)
	start_date = models.DateTimeField('date started')
	end_date = models.DateTimeField('date finished')
	
class DietItems(models.Model):
    diet = models.ForeignKey(Diet,verbose_name='Диета')
    item = models.ForeignKey(Item, verbose_name='Блюдо')
    day_of_week = models.IntegerField(verbose_name='День недели')
    eating = models.IntegerField(verbose_name='Прием пищи')
    start_date = models.DateTimeField(verbose_name='Дата начала действия')
    end_date = models.DateTimeField(verbose_name='Дата окончания действия')

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
    name = models.CharField(max_length = 100, verbose_name='Наименование')
    order = models.IntegerField(verbose_name='Порядок', blank=True)
    capacity = models.IntegerField(verbose_name='Вместимость')
    duration = models.IntegerField(verbose_name='Длительность')
    start_time = models.TimeField(verbose_name='Начало приема')
    finish_time = models.TimeField(verbose_name='Конец приема')
    optional = models.CharField(max_length=1000,verbose_name='Варианты', blank=True)
    def optional_values(self):
        return self.optional.split(',')
    def __unicode__(self):
        return self.name
    def actual_price(self):
        return self.price(datetime.date.today())
    def price(self, dt):
        list = MedicalProcedureTypePrice.objects.values("price").filter(mpt = self, add_info="", date_applied__lte = dt).order_by("-date_applied")
        if not len(list):
            return 0
        print connection.queries
        return list[0]["price"]
    def add_info_price(self, dt, add_info):
        list = MedicalProcedureTypePrice.objects.values("price").filter(date_applied__lqe = dt, add_info = add_info).order_by("-date_applied")
        if not len(list):
            return 0
        return list[0]["price"]

    class Meta:
        verbose_name = 'Тип медицинской процедуры'
        verbose_name_plural = 'Типы медицинской процедуры'

class MedicalProcedureTypePrice(models.Model):
    mpt = models.ForeignKey(MedicalProcedureType, verbose_name='Процедура')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')
    date_applied = models.DateField(verbose_name='Дата применения')
    add_info = models.CharField(max_length=50, verbose_name='Доп инфо', blank=True)
    class Meta:
        verbose_name = 'Стоимость медицинской процедуры'
        verbose_name_plural = 'Стоимости медицинской процедуры'
    def date_applied_n(self):
        return self.date_applied.strftime('%Y.%m.%d')
    def __unicode__(self):
        return self.mpt.name+"/"+self.date_applied_n()

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
    description = models.CharField(max_length = 100, blank = True)
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

class RoomPlace(models.Model):
    name = models.CharField(max_length = 100)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Расположение'
        verbose_name_plural = 'Расположения'

class Room (models.Model):
    name = models.CharField(max_length = 50, verbose_name='Наименование') # it can be room number or name of room
    room_type = models.ForeignKey(RoomType)
    description = models.CharField(max_length = 10000, blank=True)
    disabled = models.BooleanField(verbose_name='Деактивирована')
    room_place = models.ForeignKey(RoomPlace)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

class OrderType(models.Model):
    name = models.CharField(max_length = 20, verbose_name = 'Наименование')
    price = models.DecimalField(decimal_places=2,max_digits=8,verbose_name='Цена')
    def __unicode__(self):
        return self.name

class Order(models.Model):
    code = models.IntegerField(verbose_name = 'Номер заказа')
    putevka = models.CharField(max_length = 6, verbose_name = 'Номер путевки')
    patient = models.ForeignKey(Patient, verbose_name='Пациент')
    customer = models.ForeignKey(Customer, verbose_name = 'Предприятие', blank=True, null=True)
    room = models.ForeignKey(Room, verbose_name='Место расселения')
    directive = models.ForeignKey(Customer, related_name='dir', verbose_name = 'Место работы', blank= True)
    start_date = models.DateField('Дата заезда')
    end_date = models.DateField('Даты выезда')
    price = models.DecimalField(decimal_places = 2,max_digits=8, verbose_name = 'Стоимость')
    price_p = models.DecimalField(decimal_places = 2,max_digits=8, verbose_name = 'Стоимость проживания')
    is_with_child = models.BooleanField(verbose_name = 'Мать и дитя')
    payd_by_patient = models.BooleanField(verbose_name = 'Оплачивается пациентом')
    reab = models.BooleanField(verbose_name = 'Реабилитация')
    order_type = models.ForeignKey(OrderType, verbose_name='Тип заказа',blank=True, null=True)
    def __unicode__(self):
        return str(self.code)
    def start_date_n(self):
        return self.start_date.strftime('%Y.%m.%d')
    def end_date_n(self):
        return self.end_date.strftime('%Y.%m.%d')
    def start_date_cool(self):
        return self.start_date.strftime('%d.%m.%y')
    def end_date_cool(self):
        return self.end_date.strftime('%d.%m.%y')
    def end_date_cool_and_short(self):
        return self.end_date.strftime('%d.%m.%y')
    def family(self):
        if self.patient is None:
            return ""
        else:
            return self.patient.family

    #create index idx_end_date on pansionat_order (end_date);
    #create index idx_start_date on pansionat_order (start_date);
    #alter table pansionat_order add order_type_id INT;
    #create index ordertype_idx on pansionat_order (order_type_id);

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
    start_date = models.DateField(verbose_name='Дата заезда', blank=True,null=True)
    end_date = models.DateField(verbose_name='Дата отъезда', blank=True,null=True)
    name = models.CharField(max_length = 10000, blank=True)
    phone = models.CharField(max_length = 100, blank=True)
    description = models.CharField(max_length = 10000, blank=True)
    def start_date_n(self):
        return self.start_date.strfdate('%Y.%m.%d')
    def end_date_n(self):
        return self.end_date.strfdate('%Y.%m.%d')

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
