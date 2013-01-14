from django import template

register = template.Library()

@register.filter
def tab_to_nbsp(val):
    if not isinstance(val, str):
        val = u"%s" % val
    return val.replace("\t", "&nbsp" * 4)

@register.filter
def contains_nl(val):
    if not isinstance(val, str):
        val = u"%s" % val
    return "\n" in val

@register.filter
def id(obj):
    """Can't access obj._id in template. """
    return obj.get('_id')


