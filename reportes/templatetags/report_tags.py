# reportes/templatetags/report_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    """Permite usar {{ fila|get_item:columna }} cuando fila es un dict de .values()."""
    if isinstance(d, dict):
        return d.get(key, "")
    return ""
