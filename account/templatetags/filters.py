from django import template
from django.http import QueryDict

register = template.Library()


@register.filter(safe=True)
def add_attrs(field, args):
    qs = QueryDict(args)
    class_name = qs.get('class', '')
    placeholder = qs.get('placeholder', '')
    return field.as_widget(attrs={"class": class_name, "placeholder": placeholder})
