from django.db.models import *


class Doctor(Model):
    doctor_id = AutoField(primary_key=True)
    doctor_name = CharField(max_length=100, null=True)
    doctor_phone = CharField(max_length=100, null=True)
    doctor_mail = CharField(max_length=100, null=True)
    doctor_password = CharField(max_length=100, null=True)
    is_admin = BooleanField(default=False)
    special_treat_patients = ManyToManyField('Patient')


class Patient(Model):
    patient_id = AutoField(primary_key=True)
    patient_name = CharField(max_length=100, null=True)
    description = CharField(max_length=100, null=True)
    is_data_upload = BooleanField(default=False)
    teeth_slices = ManyToManyField('Slices')


class Slices(Model):
    slices_id = AutoField(primary_key=True)
    slices_position = CharField(max_length=100, null=True)
    result = CharField(max_length=100, null=True)

# Create your models here.
