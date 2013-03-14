from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from survey.models import Survey
from countries.models import Country
from tach.models import User


class Management(View):

    def get(self, request):

        countries = Country.objects.annotate(dcount=Count('surveys')) \
                                   .filter(dcount__gt=0) \
                                   .order_by('name')
        users = User.objects.annotate(dcount=Count('surveys')) \
                            .order_by('last_name', 'country')
        return render(request, 'management.html', {
            'countries': countries,
            'users': users,
        })


class AnswersByCountry(View):

    def get(self, request, country_iso):
        country = get_object_or_404(Country, pk=country_iso)
        surveys = Survey.objects.filter(country=country)
        return render(request, 'answers_by_country.html', {
            'country': country,
            'surveys': surveys,
        })