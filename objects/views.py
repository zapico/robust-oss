from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .models import Object, Measure, City, Criteria, Event, Pathway,Returntimes
from django.contrib.gis.geos import fromstr, GEOSGeometry
from .forms import FollowupUpdateForm,PathwayForm,PathwayEditForm, GeneralPathwayEditForm, GeneralPathwayForm, CriteriaForm, EventForm, ObForm, GoalUpdateForm, EventUpdateForm, CriteriaUpdateForm, LevelUpdateForm, MeasureForm, CityForm, EventFormCriteria, MalmoForm, ObjectUpdateForm, ReturnTimesForm
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar
import plotly.graph_objects as go
from decimal import Decimal
from itertools import chain
from django.db.models import Q

import csv
from django.http import StreamingHttpResponse
###################
## STATIC SITES  ##
###################
@login_required
def index(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    progress = 0
    if city.criteria_set.count() > 0: progress = progress + 33
    if city.object_set.count() > 0: progress = progress + 33
    return render(request, 'home.html', {'city': city, 'progress': progress })

@login_required
def workshops(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    return render(request, 'workshops.html', {'city': city })

@login_required
def export(request):
    return render(request, 'export.html')
######################
## EXPORT VIEWS  ##
######################
@login_required
def export_csv(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    # Get all data from UserDetail Databse Table

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="robusta_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Framgångskriteria', 'Beskrivning', "Oänskade händelse","Beskrivning","MALMÖ"])

    for cr in city.criteria_set.all() :
        writer.write([cr.name, cr.description])
        for ev in cr.event_set.all() :
            writer.writerow(["","",ev.name,ev.description,ev.returntime])

    return response

@login_required
def export_objects_csv(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    # Get all data from UserDetail Databse Table

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="robusta_export.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response,delimiter ='\t')
    writer.writerow(['Sårbar plats','Beskrivning', 'MöH', 'Koordinater',"Oänskade händelser",'Framgångskritera',"MALMÖ", "Marginal","Link"])

    for ob in city.object_set.all() :
        returntime = 0
        margin = 0
        if ob.event.returntime: returntime = ob.event.returntime
        if ob.get_margin: margin = ob.get_margin()
        writer.writerow([ob.name, ' '.join(ob.description.splitlines()), ob.altitude, ob.location, ob.event.name, ob.event.criteria.name,returntime, margin,"https://vagledning.robustklimat.se/plats/"+str(ob.id) ])


    return response
######################
## WORKSHOPS VIEWS  ##
######################
# Workshop 1A
@login_required
def workshop1A(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    return render(request, 'stad/w1a.html', {'city': city})

# Workshop 1B
@login_required
def workshop1B(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = CriteriaForm(request.POST or None)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.user = request.user
            criteria.city = request.user.city
            criteria.save()
            return redirect('workshop1B')
    form = CriteriaForm()
    return render(request, 'stad/w1b.html', {'city': city, "form": form})

# Visa alla oänskade händelser i ett område
@login_required
def workshop1C(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = EventForm(request.POST or None)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.city = request.user.city
            event.save()
            return redirect("eventer")
    form = EventForm()
    return render(request, 'stad/w1c.html', {'city': city, "form": form } )

@login_required
def workshop2(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    return render(request, 'stad/w2.html', {'city': city})

@login_required
def workshop3(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = FollowupUpdateForm(request.POST or None,instance=city)
        if form.is_valid():
            form.save()
            return redirect("workshop3")
    form = FollowupUpdateForm(instance=city)
    return render(request, 'stad/w3.html', {'city': city, "form": form})

#####################
## STRATEGY VIEWS  ##
#####################

@login_required
def strategi(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = CriteriaForm(request.POST or None)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.user = request.user
            criteria.city = request.user.city
            criteria.save()
            return redirect('workshop1B')
    form = CriteriaForm()
    return render(request, 'stad/strategi.html', {'city': city, "form": form})

@login_required
def allaplatser(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    allobjects = []
    akut = 0
    utan = 0
    total = 0
    for ob in city.object_set.all():
        if ob.event.returntime:
            print(ob.event.returntime)
            malmo = int(ob.event.returntime)
        else:
            malmo = 0
        margin = ob.get_margin()
        need = ob.needs_own()
        allobjects.append({'id': ob.id, 'name': ob.name, 'malmo': malmo, 'margin': margin, 'need': need})
        total += 1
        if margin <= 0: akut += 1
        if need == 2: utan += 1
    def myFunc(e):
        return e['malmo']
    allobjects.sort(reverse=True, key=myFunc)
    return render(request, 'objects/all.html', {'city': city, 'allobjects': allobjects, "total": total, "utan": utan, "akut": akut } )

@login_required
def allaplatser_margin(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    allobjects = []
    akut = 0
    utan = 0
    total = 0
    for ob in city.object_set.all():
        if ob.event.returntime:
            malmo = ob.event.returntime
        else:
            malmo = 0
        margin = ob.get_margin()
        need = ob.needs_own()
        allobjects.append({'id': ob.id, 'name': ob.name, 'malmo': malmo,'margin': margin, 'need': need })
        total += 1
        if margin <= 0: akut += 1
        if need == 2: utan += 1
    def myFunc(e):
        return e['margin']
    allobjects.sort(reverse=False, key=myFunc)
    return render(request, 'objects/all.html', {'city': city, 'allobjects': allobjects, "total": total, "utan": utan, "akut": akut } )

@login_required
def allaplatser_atgard(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    allobjects = []
    akut = 0
    utan = 0
    total = 0
    for ob in city.object_set.all():
        if ob.event.returntime:
            malmo = ob.event.returntime
        else:
            malmo = 0
        margin = ob.get_margin()
        need = ob.needs_own()
        allobjects.append({'id': ob.id, 'name': ob.name, 'malmo': malmo,'margin': margin, 'need': need })
        total += 1
        if margin <= 0: akut += 1
        if need == 2: utan += 1
    def myFunc(e):
        return e['need']
    allobjects.sort(reverse=True, key=myFunc)
    return render(request, 'objects/all.html', {'city': city, 'allobjects': allobjects, "total": total, "utan": utan, "akut": akut } )

@login_required
def map(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    allobjects = []
    for ob in city.object_set.all():
        if ob.event.returntime:
            malmo = ob.event.returntime
        else:
            malmo = 0
        allobjects.append({'id': ob.id, 'name': ob.name, 'malmo': malmo })
    def myFunc(e):
        return e['malmo']
    allobjects.sort(reverse=True, key=myFunc)
    return render(request, 'stad/map.html', {'city': city, 'allobjects': allobjects } )

@login_required
def pathway(request, pathway_id=None):
    city = get_object_or_404(City, pk=request.user.city.id)
    # Get all places and get their margin, order by less margin to more
    allobjects = []
    for ob in city.object_set.all():
        allobjects.append({'id': ob.id, 'name': ob.name, 'margin': ob.get_margin(), 'need': ob.needs_own() })
    def myFunc(e):
        return e['margin']
    allobjects.sort(reverse=False, key=myFunc)

    # Get all general measures and add them to arrays for visualization
    measures = Measure.objects.filter(city = city.id).filter(general = True).order_by('-level')
    x_data = []
    y_data = []
    for measure in measures:
        y_data.append(measure.name)
        x_data.append(Decimal(measure.level))
    graphs = []
    graphs.append(
        go.Bar(x=x_data, y=y_data,
            orientation='h', name='', opacity=0.3
        ))
    # Create pathway graph if there is a pathway.
    plot_path = ""
    paths = city.pathway_set.filter(object__isnull = True)
    if(paths):
        for path in paths:
            pathway = get_object_or_404(Pathway, pk=path.id)
            smallestmargin = get_object_or_404(Object, pk=allobjects[0]['id'])
            waterfall_x = []
            waterfall_y = []
            waterfall_measure = []
            waterfall_x.append("Marginal")
            waterfall_y.append(smallestmargin.get_margin())
            waterfall_measure.append("relative")
            tot=Decimal(smallestmargin.get_margin())
            if pathway.steg1:
                steg1 = get_object_or_404(Measure, pk=pathway.steg1.id)
                waterfall_x.append(steg1.name)
                waterfall_y.append(Decimal(steg1.level)-tot)
                waterfall_measure.append("relative")
                tot=Decimal(steg1.level)
            if pathway.steg2:
                steg2 = get_object_or_404(Measure, pk=pathway.steg2.id)
                waterfall_x.append(steg2.name)
                waterfall_y.append(Decimal(steg2.level)-tot)
                waterfall_measure.append("relative")
                tot=Decimal(steg2.level)
            if pathway.steg3:
                steg3 = get_object_or_404(Measure, pk=pathway.steg3.id)
                waterfall_x.append(steg3.name)
                waterfall_y.append(Decimal(steg3.level)-tot)
                waterfall_measure.append("relative")
            graphs.append(
                go.Waterfall(name = "Pathway", orientation = "h", opacity=1,
                measure = waterfall_measure,
                y = waterfall_x,
                x = waterfall_y,
                connector = {"line":{"width":4, "color":"rgb(0, 0, 0)", "dash":"solid"}}
                ))
    #graphs.update_xaxes(range=[0,city.level])
    # Setting layout of the figure.
    layout = {
        'title': '',
        'xaxis_title': 'meter vattenhöjning',
    }
    # Getting HTML needed to render the plot.
    plot_path = plot({'data': graphs, 'layout': layout}, output_type='div')
    # Add form create or edit
    if request.method == "POST":
        if(pathway_id):
            path=get_object_or_404(Pathway, pk=pathway_id)
            form = GeneralPathwayEditForm(request.POST, instance=path, city_id=city.id)
        else:
            form = GeneralPathwayForm(request.POST,city_id=city.id)
        if form.is_valid():
            path = form.save(commit=False)
            path.user = request.user
            path.city = request.user.city
            path.save()
            return redirect("pathway")
    if(pathway_id):
        path=get_object_or_404(Pathway, pk=pathway_id)
        form = GeneralPathwayEditForm(instance=path ,city_id=city.id)
    else:
        form = GeneralPathwayForm(city_id=city.id)

    return render(request, 'stad/pathway.html', {'city': city, 'allobjects': allobjects,'paths':paths,'form': form, 'plot_path': plot_path, 'pathway_id':pathway_id})


#######################
## INDIVIDUAL VIEWS  ##
#######################
@login_required
def paths(request, object_id, pathway_id=None):
    #Secure that it's on same city
    city = get_object_or_404(City, pk=request.user.city.id)
    object = get_object_or_404(Object, pk=object_id)
    if object.city.id != city.id:
        return redirect('index')
    x_data = []
    y_data = []

    measures = object.measure_set.all().order_by('-level')
    gen_measures = Measure.objects.filter(city = city.id).filter(general = True)

    for measure in measures:
        y_data.append(measure.name)
        x_data.append(Decimal(measure.level))

    # Create pathway graph
    plot_path = ""
    graphs = []
    graphs.append(
        go.Bar(x=x_data, y=y_data,
            orientation='h', name='', opacity=0.3
    ))

    paths = object.pathway_set.all()
    if(paths):
        for pathway in paths:
            waterfall_x = []
            waterfall_y = []
            waterfall_measure = []
            waterfall_x.append("Marginal")
            waterfall_y.append(object.get_margin())
            waterfall_measure.append("relative")
            tot=Decimal(object.get_margin())
            if pathway.steg1:
                steg1 = get_object_or_404(Measure, pk=pathway.steg1.id)
                waterfall_x.append(steg1.name)
                waterfall_y.append(Decimal(steg1.level)-tot)
                waterfall_measure.append("relative")
                tot=Decimal(steg1.level)
            if pathway.steg2:
                steg2 = get_object_or_404(Measure, pk=pathway.steg2.id)
                waterfall_x.append(steg2.name)
                waterfall_y.append(Decimal(steg2.level)-tot)
                waterfall_measure.append("relative")
                tot=Decimal(steg2.level)
            if pathway.steg3:
                steg3 = get_object_or_404(Measure, pk=pathway.steg3.id)
                waterfall_x.append(steg3.name)
                waterfall_y.append(Decimal(steg3.level)-tot)
                waterfall_measure.append("relative")
            graphs.append(
                go.Waterfall(name = "20", orientation = "h",
                measure = waterfall_measure,
                y = waterfall_x,
                x = waterfall_y,
                connector = {"line":{"width":4, "color":"rgb(0, 0, 0)", "dash":"solid"}}
            ))
    #graphs.update_xaxes(range=[0,city.level])
    # Setting layout of the figure.
    layout = {
        'title': '',
        'xaxis_title': 'meter medelvattenhöjning',
    }
    # Getting HTML needed to render the plot.
    plot_path = plot({'data': graphs, 'layout': layout}, output_type='div')

    # Create barchart for all measures
    plot_div = plot([Bar(x=x_data, y=y_data,
                        orientation='h', name='',
                        meta = {
                        'title': 'Date test',
                        'xaxis': {'range': [0,10]},
                        'yaxis': {'range': [0,10]},
                        })],
                        output_type='div')

    if request.method == "POST":
        if(pathway_id):
            print("Hello")
            path=get_object_or_404(Pathway, pk=pathway_id)
            form = PathwayEditForm(request.POST, instance=path,city_id=city.id, object_id=object.id)
        else:
            form = PathwayForm(request.POST,city_id=city.id, object_id=object.id)
        if form.is_valid():
            pathw = form.save(commit=False)
            print(pathw)
            pathw.user = request.user
            pathw.city = request.user.city
            pathw.object = object
            pathw.save()
            return redirect("paths", object.id)
        else:
            print(form.errors.as_data())
    if(pathway_id):
        path=get_object_or_404(Pathway, pk=pathway_id)
        form = PathwayEditForm(instance=path, city_id=city.id, object_id=object.id)
    else:
        form = PathwayForm(city_id=city.id, object_id=object.id)
    return render(request, 'objects/pathways.html', {'object': object, 'path':pathway_id,'form': form, 'plot_div': plot_div, 'plot_path': plot_path})

@login_required
def object(request, object_id):
    #Secure that it's on same city
    city = get_object_or_404(City, pk=request.user.city.id)
    object = get_object_or_404(Object, pk=object_id)
    if object.city.id != city.id:
        return redirect('index')
    # Get returntimes for the city
    returntimes = get_object_or_404(Returntimes, city=city.id)
    # Get Malmö for the event
    malmo = object.event.returntime
    # Get the relevant returntime based on malmö
    if malmo:
        returntime = getattr(returntimes, 'y'+str(malmo))
    else:
        returntime = 0
    # Calculate margin
    margin = object.altitude - returntime
    generalmeasures = city.measure_set.filter(general=True);
    if request.method == "POST":
        form = MeasureForm(request.POST or None)
        if form.is_valid():
            measure = form.save(commit=False)
            measure.user = request.user
            measure.city = request.user.city
            measure.general = False
            measure.save()
            measure.object.add(object)

            return redirect("object", object.id)
    form = MeasureForm()
    return render(request, 'objects/object_w2.html', {'object': object, 'form': form, 'margin': margin, 'generalmeasures': generalmeasures})


@login_required
def criteria(request, criteria_id):
    criteria = get_object_or_404(Criteria, pk=criteria_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if criteria.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form = EventFormCriteria(request.POST or None)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.city = request.user.city
            event.criteria = criteria
            event.save()
            return redirect("criteria", criteria.id)
    form = EventFormCriteria()
    return render(request, 'stad/criteria.html', {'criteria': criteria, 'form': form, "back":request.session['previo'] })

@login_required
def handlingar(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    return render(request, 'stad/handlingar.html', {'city': city } )

# Visa en specifik oänskade händelse
@login_required
def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if event.city.id != city.id:
        return redirect('index')
    allobjects = []
    for ob in event.object_set.all():
        allobjects.append({'id': ob.id, 'name': ob.name, 'margin': ob.get_margin() })
    def myFunc(e):
        return e['margin']
    allobjects.sort(reverse=False, key=myFunc)
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form = MalmoForm(request.POST,instance=event)
        if form.is_valid():
            form.save()
    #        return redirect('event', event.id)
    form = MalmoForm(instance=event)
    return render(request, 'stad/event.html', {'event': event, 'form': form, 'city': city, "back":request.session['previo'], 'allobjects':allobjects } )


# Visa en specifik oänskade händelse
@login_required
def measure(request, measure_id):
    measure = get_object_or_404(Measure, pk=measure_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if measure.city.id != city.id:
        return redirect('index')
    allobjects = []
    for ob in measure.object.all():
        margin = ob.get_margin()
        newmargin = round(Decimal(measure.level) + margin, 2)
        allobjects.append({'id': ob.id, 'name': ob.name, 'margin': margin, 'newmargin': newmargin })
    def myFunc(e):
        return e['margin']
    allobjects.sort(reverse=False, key=myFunc)

    no_objects = []
    for ob in city.object_set.filter(~Q(measure__id = measure_id)):
        no_objects.append({'id': ob.id, 'name': ob.name, 'margin': ob.get_margin() })
    def myFunc(e):
        return e['margin']
    no_objects.sort(reverse=False, key=myFunc)

    return render(request, 'objects/measure.html', {'measure': measure, 'city': city, 'allobjects':allobjects ,'no_objects':no_objects} )




###################
## CREATE VIEWS  ##
###################

# Create a new object
@login_required
def new_object(request, event_id):
    city = get_object_or_404(City, pk=request.user.city.id)
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        form = ObForm(request.POST or None)
        if form.is_valid():
            object = form.save(commit=False)
            object.user = request.user
            object.city = request.user.city
            object.event = event
            object.save()
            return redirect("event", event.id)
    form = ObForm()
    return render(request, 'objects/new_object.html', {'city': city, "form": form, "event": event } )

@login_required
def new_measure(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    measures = Measure.objects.filter(city = city.id).filter(general = True)
    measures_ob = Measure.objects.filter(city = city.id).filter(general=False)
    if request.method == "POST":
        form = MeasureForm(request.POST or None)
        if form.is_valid():
            measure = form.save(commit=False)
            measure.user = request.user
            measure.city = request.user.city
            measure.general = True
            measure.save()
            if measure.general:
                for ob in city.object_set.all():
                    ob.measure_set.add(measure)
            return redirect("new_measure")
    form = MeasureForm()
    return render(request, 'objects/new_measure.html', {'city': city, "form": form, "measures": measures, "measures_ob": measures_ob } )

#################
## EDIT VIEWS  ##
#################
@login_required
def connect_measure(request, measure_id, object_id):
    measure = get_object_or_404(Measure, pk=measure_id)
    object = get_object_or_404(Object, pk=object_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    measure.object.add(object)
    return redirect("object", object.id)

def remove_measure(request, measure_id, object_id):
    measure = get_object_or_404(Measure, pk=measure_id)
    object = get_object_or_404(Object, pk=object_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    measure.object.remove(object)
    return redirect("object", object.id)


@login_required
def edit_measure(request, measure_id):
    measure = get_object_or_404(Measure, pk=measure_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if measure.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form = MeasureForm(request.POST,instance=measure)
        if form.is_valid():
            form.save()
            return  HttpResponseRedirect(request.session['previo'])
    form = MeasureForm(instance=measure)
    return render(request, 'edit/measure.html', {'measure': measure, "form": form, "back": request.session['previo']})


@login_required
def delete_measure(request, measure_id):
    measure = get_object_or_404(Measure, pk=measure_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    steg1 = Pathway.objects.filter(steg1=measure.id).count()
    steg2 = Pathway.objects.filter(steg2=measure.id).count()
    steg3 = Pathway.objects.filter(steg3=measure.id).count()
    used = int(steg1) + int(steg2) + int(steg3)
    #Security
    if measure.city.id != city.id:
        return redirect('index')
    if request.method == 'POST':
        measure.delete()
        return redirect('new_measure')
    return render(request, 'edit/delete_measure.html', {'measure': measure, 'used': used })

@login_required
def edit_criteria(request, criteria_id):
    criteria = get_object_or_404(Criteria, pk=criteria_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if criteria.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form = CriteriaUpdateForm(request.POST,instance=criteria)
        if form.is_valid():
            form.save()
            return  HttpResponseRedirect(request.session['previo'])
    form = CriteriaUpdateForm(instance=criteria)
    return render(request, 'edit/criteria.html', {'criteria': criteria, "form": form, "back": request.session['previo']})


@login_required
def delete_criteria(request, criteria_id):
    criteria = get_object_or_404(Criteria, pk=criteria_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if criteria.city.id != city.id:
        return redirect('index')
    if request.method == 'POST':
        criteria.delete()
        return redirect('/handelser')
    return render(request, 'edit/delete_criteria.html', {'criteria': criteria,})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if event.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return  HttpResponseRedirect(request.session['previo'])
    form = EventUpdateForm(instance=event)
    return render(request, 'edit/event.html', {'event': event, "form": form, "back": request.session['previo']})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    cr=event.criteria.id
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if event.city.id != city.id:
        return redirect('index')
    if request.method == 'POST':
        event.delete()
        return redirect('criteria',cr)
    return render(request, 'edit/delete_event.html', {'event': event,})

# Edit fokusfråga
@login_required
def edit_goal(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = GoalUpdateForm(request.POST or None,instance=city)
        if form.is_valid():
            form.save()
            return redirect("workshop1A")
    form = GoalUpdateForm(instance=city)
    return render(request, 'edit/goal.html', {'city': city, "form": form } )

@login_required
def edit_level(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == "POST":
        form = LevelUpdateForm(request.POST or None,instance=city)
        if form.is_valid():
            form.save()
            return redirect("workshop1C")
    form = LevelUpdateForm(instance=city)
    return render(request, 'edit/level.html', {'city': city, "form": form } )

@login_required
def edit_omrade(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            return redirect("workshop1A")
    form = CityForm(instance=city)
    return render(request, 'edit/location.html', {'city': city, "form": form } )

@login_required
def edit_object(request, object_id):
    object = get_object_or_404(Object, pk=object_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if object.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form = ObjectUpdateForm(request.POST,instance=object)
        if form.is_valid():
            form.save()
            return  HttpResponseRedirect(request.session['previo'])
    form = ObjectUpdateForm(instance=object)
    return render(request, 'edit/object.html', {'object': object, "form": form, "back": request.session['previo']})

@login_required
def delete_object(request, object_id):
    object = get_object_or_404(Object, pk=object_id)
    ev=object.event.id
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if object.city.id != city.id:
        return redirect('index')
    if request.method == 'POST':
        object.delete()
        return redirect('event',ev)
    return render(request, 'edit/delete_object.html', {'object': object,})

@login_required
def delete_pathway(request, pathway_id):
    pathway = get_object_or_404(Pathway, pk=pathway_id)
    city = get_object_or_404(City, pk=request.user.city.id)
    #Security
    if pathway.city.id != city.id:
        return redirect('index')
    if request.method == 'GET':
        request.session['previo'] = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        pathway.delete()
        return  HttpResponseRedirect(request.session['previo'])
    return render(request, 'edit/delete_pathway.html', {'pathway': pathway,"back": request.session['previo']})


@login_required
def edit_times(request):
    city = get_object_or_404(City, pk=request.user.city.id)
    times = get_object_or_404(Returntimes, city=city.id)
    if request.method == "POST":
        form = ReturnTimesForm(request.POST or None,instance=times)
        if form.is_valid():
            form.save()
            return redirect("workshop1A")
    form = ReturnTimesForm(instance=times)
    return render(request, 'edit/times.html', {'city': city, "form": form } )
