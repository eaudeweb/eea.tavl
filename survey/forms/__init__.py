from django import forms
from survey.models import Survey, Language


class SectionA(forms.Form):

    EDIT_TEMPLATE = 'section_a/form.html'

    VIEW_TEMPLATE = 'section_a/view.html'

    status = forms.ChoiceField(choices=Survey.STATUS_CHOICES, widget=forms.RadioSelect)

    title = forms.CharField(max_length=256)

    english_title = forms.CharField(max_length=256, required=False)

    year = forms.IntegerField(required=False)

    parts_considered = forms.MultipleChoiceField(choices=Survey.TRANSPORT_PARTS,
         widget=forms.CheckboxSelectMultiple)

    transport_modes = forms.MultipleChoiceField(choices=Survey.TRANSPORT_MODES,
        widget=forms.CheckboxSelectMultiple)

    climate_change_impacts = forms.MultipleChoiceField(choices=Survey.IMPACTS,
        label='Climate change/extreme weather impact(s) considered for transport (Tick any relevant categories)',
        widget=forms.CheckboxSelectMultiple,)

    responsible_organisation = forms.CharField(max_length=256, required=False)

    link = forms.CharField(max_length=256, required=False)

    def clean_parts_considered(self):
        parts_considered = self.cleaned_data['parts_considered']
        parts_considered_hstore = {i:'1' for i in parts_considered}
        return parts_considered_hstore

    def clean_transport_modes(self):
        transport_modes = self.cleaned_data['transport_modes']
        transport_modes_hstore = {i:'1' for i in transport_modes}
        return transport_modes_hstore

    def clean_climate_change_impacts(self):
        climate_change_impacts = self.cleaned_data['climate_change_impacts']
        climate_change_impacts_hstore = {i:'1' for i in climate_change_impacts}
        return climate_change_impacts_hstore

    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        return survey


class SectionB(SectionA):

    language = forms.ChoiceField()

    contact = forms.CharField(max_length=256, required=False)

    def __init__(self, *args, **kwargs):
        super(SectionB, self).__init__(*args, **kwargs)
        self.fields.pop('status')
        self.fields.pop('english_title')
        languages = [(l.iso, l.title) for l in Language.objects.all()]
        self.fields['language'].choices = languages

    def save(self, user, country, category):
        language = Language.objects.get(pk=self.cleaned_data['language'])
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            title=self.cleaned_data['title'],
            language= language,
            year=self.cleaned_data['year'],
            parts_considered=self.cleaned_data['parts_considered'],
            transport_modes=self.cleaned_data['transport_modes'],
            climate_change_impacts=self.cleaned_data['climate_change_impacts'],
            responsible_organisation=self.cleaned_data['responsible_organisation'],
            contact=self.cleaned_data['contact'],
            link=self.cleaned_data['link']
        )
        return survey


class SectionB4(SectionA):

    focus = forms.CharField(max_length=256, required=False)

    def __init__(self, *args, **kwargs):
        super(SectionB4, self).__init__(*args, **kwargs)
        self.fields.pop('status')
        self.fields.pop('english_title')

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            title=self.cleaned_data['title'],
            focus=self.cleaned_data['focus'],
            year=self.cleaned_data['year'],
            parts_considered=self.cleaned_data['parts_considered'],
            transport_modes=self.cleaned_data['transport_modes'],
            climate_change_impacts=self.cleaned_data['climate_change_impacts'],
            responsible_organisation=self.cleaned_data['responsible_organisation'],
            contact=self.cleaned_data['contact'],
            link=self.cleaned_data['link']
        )
        return survey
