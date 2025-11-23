from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    """Permite acceder a un valor de un diccionario en las plantillas."""
    if isinstance(d, dict):
        return d.get(key, "")
    return ""
