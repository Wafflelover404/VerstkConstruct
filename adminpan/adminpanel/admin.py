from django.contrib import admin
from .models import Component
from django import forms

TYPES = [('text', 'Text'), ('image', 'Image')]


class ComponentForm(forms.ModelForm):
    type = forms.ChoiceField(choices=TYPES)

    class Meta:
        model = Component
        fields = '__all__'


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    form = ComponentForm
