from django import forms
from .models import Criteria, Event, Object, City, Measure, Pathway, Returntimes
from leaflet.forms.widgets import LeafletWidget
from itertools import chain
from django.shortcuts import get_object_or_404

class ObForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
            widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Beskrivning",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    altitude = forms.DecimalField(
        required=True,
            widget=forms.widgets.NumberInput(
            attrs={
                "class": "input is-success is-small",
            }
        ),
        label="Meter över havet (rH2000)",
    )

    class Meta:
        model = Object
        exclude = ("user", "city", "event", "marginal")
        widgets = {'location': LeafletWidget()}

class CriteriaForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    class Meta:
        model = Criteria
        exclude = ("user", "city")

class EventFormCriteria(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    criteria = forms.Select(
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['criteria'].choices=[(item.pk, item) for item in Criteria.objects.filter(City=self.instance.city_id)]


    class Meta:
        model = Event
        exclude = ("user", "city", "returntime", "criteria")

class MalmoForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ("user", "city", "name", "description", "criteria")

class EventForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    criteria = forms.Select(
        #choices=[(item.pk, item) for item in Criteria.objects.filter(city = 6)],
    )


    class Meta:
        model = Event
        exclude = ("user", "city", "returntime")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['criteria'].choices=[(item.pk, item) for item in Criteria.objects.filter(city=self.instance.city_id)]
        self.fields['criteria'].label="Framgångskriteria"
        
class MeasureForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    level = forms.DecimalField(
        required=True,
            widget=forms.widgets.NumberInput(
            attrs={
                "class": "input is-success is-small",
            }
        ),
        label="Havsnivåhöjning (meter) som åtgärden är effektiv mot:",
    )
    cost = forms.ChoiceField(
        required=False,
        choices=[(1, "Billigt"),(2, "Relativt billigt"),(3, "Mellan"),(4, "Relativt dyrt"),(5, "Dyrt")],
        widget=forms.widgets.RadioSelect(
            attrs={
                "placeholder": "Svårighet",
                "class": "checkbox is-primary is-small",
            }
        ),
        label="",

    )


    class Meta:
        model = Measure
        exclude = ("user", "city", "object", "general")

class FollowupUpdateForm(forms.ModelForm):
    followup = forms.CharField(
        required=False,
            widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Uppföljning",
                "class": "textarea is-success is-big",
            }
        ),
        label="",
    )
    class Meta:
        model = City
        exclude = ("name", "location","description","area", "level", "focus")

class GoalUpdateForm(forms.ModelForm):
    focus = forms.CharField(
        required=False,
            widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Fokusfråga",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    class Meta:
        model = City
        exclude = ("name", "location","description","area", "level", "followup")

class LevelUpdateForm(forms.ModelForm):
    level = forms.DecimalField(
        required=False,
            widget=forms.widgets.NumberInput(
            attrs={
                "class": "input is-success is-small",
            }
        ),
        label="Skyddsnivå i meter",
    )
    class Meta:
        model = City
        exclude = ("name", "location","description","area", "focus", "followup")

class EventUpdateForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    criteria = forms.Select(

        #choices=[(item.pk, item) for item in Criteria.objects.filter(city = 6)],
    )
    class Meta:
        model = Event
        exclude = ("city", "user", "returntime")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['criteria'].choices=[(item.pk, item) for item in Criteria.objects.filter(city=self.instance.city_id)]
        self.fields['criteria'].label="Framgångskriteria"

class ObjectUpdateForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
            widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Beskrivning",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    altitude = forms.DecimalField(
        required=False,
            widget=forms.widgets.NumberInput(
            attrs={
                "class": "input is-success is-small",
            }
        ),
        label="Meter över havet (rH2000)",
    )
    class Meta:
        model = Object
        exclude = ("user", "city", "event", "marginal")
        widgets = {'location': LeafletWidget()}

class CriteriaUpdateForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Förklaring",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    class Meta:
        model = Criteria
        exclude = ("city", "user")

class CityForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(
            attrs={
                "placeholder": "Namn",
                "class": "input is-success is-medium",
            }
        ),
        label="",
    )
    description = forms.CharField(
        required=False,
            widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Beskrivning",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )

    class Meta:
        model = City
        exclude = ("location","focus","level", "followup")
        widgets = {'area': LeafletWidget()}

class PathwayForm(forms.ModelForm):
    class Meta:
        model = Pathway
        exclude = ("user", "city", "object", "cost", "level")
    def __init__(self,*args,**kwargs):
        self.city_id = kwargs.pop('city_id')
        self.object_id = kwargs.pop('object_id')
        queryset = Measure.objects.filter(object = self.object_id)
        super(PathwayForm,self).__init__(*args,**kwargs)
        description = forms.CharField(required=False,widget=forms.widgets.Textarea(attrs={"placeholder": "Förklaring","class": "textarea is-success is-small",}),label="",)
        self.fields['steg1'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select())
        self.fields['steg2'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)
        self.fields['steg3'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)
#ProductMetaInlineFormset = inlineformset_factory(Object, Pathway, form=PathwayForm, extra=5)
class PathwayEditForm(forms.ModelForm):
    class Meta:
        model = Pathway
        exclude = ("user", "city", "object", "cost", "level")
    def __init__(self,*args,**kwargs):
        self.city_id = kwargs.pop('city_id')
        self.object_id = kwargs.pop('object_id')
        queryset = Measure.objects.filter(object = self.object_id)
        super(PathwayEditForm,self).__init__(*args,**kwargs)
        description = forms.CharField(required=False,widget=forms.widgets.Textarea(attrs={"placeholder": "Förklaring","class": "textarea is-success is-small",}),label="",)
        self.fields['steg1'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select())
        self.fields['steg2'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)
        self.fields['steg3'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)

class GeneralPathwayForm(forms.ModelForm):
    class Meta:
        model = Pathway
        exclude = ("user", "city", "object", "cost", "level")
    def __init__(self,*args,**kwargs):
        self.city_id = kwargs.pop('city_id')
        queryset = Measure.objects.filter(city = self.city_id).filter(general = True)
        super(GeneralPathwayForm,self).__init__(*args,**kwargs)
        description = forms.CharField(required=False,widget=forms.widgets.Textarea(attrs={"placeholder": "Förklaring","class": "textarea is-success is-small",}),label="",)
        self.fields['steg1'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select())
        self.fields['steg2'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)
        self.fields['steg3'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)

class GeneralPathwayEditForm(forms.ModelForm):
    class Meta:
        model = Pathway
        exclude = ("user", "city", "object", "cost", "level")
    def __init__(self,*args,**kwargs):
        self.city_id = kwargs.pop('city_id')
        queryset = Measure.objects.filter(city = self.city_id).filter(general = True)
        super(GeneralPathwayEditForm,self).__init__(*args,**kwargs)
        description = forms.CharField(required=False,widget=forms.widgets.Textarea( attrs={"placeholder": "Förklaring","class": "textarea is-success is-small",}),label="",)
        self.fields['steg1'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select())
        self.fields['steg2'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)
        self.fields['steg3'] = forms.ModelChoiceField(queryset=queryset, widget=forms.Select(),required = False)

class ReturnTimesForm(forms.ModelForm):

    y1 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/1",)
    y2 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/2",)
    y5 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/5",)
    y10 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/10",)
    y20 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/20",)
    y50 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/50",)
    y100 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/100",)
    y200 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/200",)
    y500 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/500",)
    y1000 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/1000",)
    y10000 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/10000",)
    y100000 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/100000",)
    y1000000 = forms.DecimalField(widget=forms.widgets.NumberInput(attrs={"class": "input is-success is-small",}),label="1/1000000",)
    description = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Kommentarer",
                "class": "textarea is-success is-small",
            }
        ),
        label="",
    )
    class Meta:
        model = Returntimes
        exclude = ("city","id")
