import string
from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count
from sugar import markup
from tach.frame import get_current_request
from tach.models import User


register = template.Library()


@register.filter
def get_answers(section, category):
    return section.filter(category=category)


@register.filter
def get_answers_for_user(section, category):
    request = get_current_request()
    return section.filter(category=category, user=request.account)


@register.assignment_tag
def assign(value):
    return value


@register.filter
def pretty_hstore(value):
    if not isinstance(value, dict):
        if value is None:
            return '-'
        if not isinstance(value, basestring):
            value = str(value)
        return string.capwords(value).replace('_', ' ')
    page = markup.page()
    page.ul()
    for k, v in value.items():
        if v == '1':
            page.li()
            page.span(string.capwords(k).replace('_', ' '))
            page.li.close()
    page.ul.close()
    return mark_safe(page)


@register.filter
def getattribute(value, name):
    return getattr(value, name, None)


@register.filter
def keyvalue(value, key):
    return value[key]


@register.filter
def users_for_country(country):
    return User.objects.annotate(count=Count('surveys')).filter(country=country)


@register.assignment_tag
def get_survey_form(category):
    return category.get_widget()()


