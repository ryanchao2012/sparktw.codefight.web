from django import template


register = template.Library()


@register.filter
def pretty(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds - hours * 3600) // 60
    seconds = (total_seconds - hours * 3600 - minutes * 60)

    return '{} hr {} min {} sec'.format(hours, minutes, seconds)
