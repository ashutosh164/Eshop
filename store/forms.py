from django import forms
from.models import *


class TaskForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class CreateCustomer(forms.ModelForm):
    class Meta:
        model = Customer
        fields =  '__all__'


class Billing(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['status']