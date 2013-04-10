import tempfile
from collections import defaultdict
from path import path
import xlwt

from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils.text import capfirst
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator

from survey.models import Survey, Category
from countries.models import Country
from tach.models import User
from sugar.views import auth_admin_required


class Management(View):

    @method_decorator(auth_admin_required)
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
        coverage['total'] = 100
        return coverage


class AnswersByCountry(View):

    @method_decorator(auth_admin_required)
    def get(self, request, country_iso):
        country = get_object_or_404(Country, pk=country_iso)
        surveys = Survey.objects.filter(country=country).order_by('category')
        return render(request, 'answers_by_country.html', {
            'country': country,
            'surveys': surveys,
            'view_answer': True,
        })


class AnswersByQuestion(View):

    @method_decorator(auth_admin_required)
    def get(self, request):
        surveys = Survey.objects.order_by('category', 'country')
        return render(request, 'answers_by_question.html', {
            'surveys': surveys,
        })


class Download(View):


    def read_file(self, f):
        while True:
            data = f.read(131072)
            if data:
                yield data
            else:
                break
        f.close()

    @method_decorator(auth_admin_required)
    def get(self, request):
        from django.http import HttpResponse
        surveys = Survey.objects.all()
        temp = path(tempfile.mkdtemp())
        filename = temp / 'survey.xls'

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Survey')

        # adding columns
        columns = Survey.get_fields_for_serialization()
        for i, field in enumerate(columns):
            ws.write(0, i, capfirst(field.verbose_name))
        # adding rows
        for i, survey in enumerate(surveys):
            for j, field in enumerate(columns):
                ws.write(i+1, j, survey.serialize_field(field))

        wb.save(filename)

        # keep the file open until the download is finished
        # temp folder will be deleted after
        try:
            file_path = open(filename)
        finally:
            temp.rmtree()

        response = StreamingHttpResponse(self.read_file(file_path),
                                         content_type='application/xls')
        response['Content-Disposition'] = 'attachment; filename="survey.xls"'
        return response


