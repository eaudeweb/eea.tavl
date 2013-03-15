from collections import defaultdict

from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from survey.models import Survey, Category
from countries.models import Country
from tach.models import User


class Management(View):

    def get(self, request):

        countries = Country.objects.annotate(dcount=Count('surveys')) \
                                   .filter(dcount__gt=0) \
                                   .order_by('name')
        users = User.objects.annotate(dcount=Count('surveys')) \
                            .order_by('last_name', 'country')
        coverage = self.get_coverage_data()

        return render(request, 'management.html', {
            'countries': countries,
            'coverage': coverage,
            'users': users,
        })

    def get_coverage_data(self):
        total = Category.objects.count()
        categs = Category.objects.values('id', 'surveys__country') \
            .annotate(dcount=Count('surveys')).filter(dcount__gt=0)

        map_categs = defaultdict(list)
        for categ in categs:
            map_categs[categ['surveys__country']].append(categ['id'])
        coverage = {k:float((len(v)*100)/total) for k, v in map_categs.items()}
        coverage['total'] = total
        return coverage


class AnswersByCountry(View):

    def get(self, request, country_iso):
        country = get_object_or_404(Country, pk=country_iso)
        surveys = Survey.objects.filter(country=country).order_by('category')
        return render(request, 'answers_by_country.html', {
            'country': country,
            'surveys': surveys,
            'view_answer': True,
        })