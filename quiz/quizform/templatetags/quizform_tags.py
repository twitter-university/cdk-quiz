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


@register.filter
def status_class(status):
    """Return bootstrap class name mapping to status. """
    vals = {True: "btn-success", False: 'btn-danger'}
    return vals.get(status, 'btn-warning')

@register.filter
def status(status):
    """Return bootstrap class name mapping to status. """
    vals = {True: "Pass", False: 'Fail'}
    print repr(status)
    return vals.get(status, 'Ungraded')


