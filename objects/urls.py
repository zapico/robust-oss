from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('workshops', views.workshops, name='workshops'),
    path("accounts/", include("django.contrib.auth.urls")),
    #Workshops
    path('export/sammanfattning/', views.export_csv, name='csv_sammanfattning'),
    path('export/platser/', views.export_objects_csv, name='csv_sammanfattning'),
    path('workshop1B/', views.workshop1B, name='workshop1B'),
    path('workshop1C/', views.workshop1C, name='workshop1C'),
    path('workshop2/', views.workshop2, name='workshop2'),
    path('workshop3/', views.workshop3, name='workshop3'),
    #Strategy
    path('karta/', views.map, name='karta'),
    path('platser/', views.allaplatser, name='karta'),
    path('platser/malmo', views.allaplatser, name='karta'),
    path('platser/marginal', views.allaplatser_margin, name='karta'),
    path('platser/atgard', views.allaplatser_atgard, name='karta'),
    path('handlingar/', views.handlingar, name='handlingar'),
    path('handelser/', views.strategi, name='handelser'),
    path('pathway/<int:pathway_id>', views.pathway, name='pathway'),
    path('pathway/', views.pathway, name='pathway'),
    path('export/', views.export, name='export'),
    # See specific things
    path('event/<int:event_id>/', views.event, name='event'),
    path('plats/<int:object_id>/', views.object, name='object'),
    path('pathways/<int:object_id>/', views.paths, name='paths'),
    path('pathways/<int:object_id>/<int:pathway_id>', views.paths, name='paths'),
    path('kriterium/<int:criteria_id>/', views.criteria, name='criteria'),
    path('atgard/<int:measure_id>/', views.measure, name='measure'),
    # New things
    path('nytt_objekt/<int:event_id>/', views.new_object, name='new_object'),
    path('ny_atgard/', views.new_measure, name='new_measure'),
    path('atgarder/', views.new_measure, name='new_measure'),
    # Edit things
    path('edit/information/', views.workshop1A, name='workshop1A'),
    path('edit/event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('edit/kriteria/<int:criteria_id>/', views.edit_criteria, name='edit_criteria'),
    path('edit/plats/<int:object_id>/', views.edit_object, name='edit_object'),
    path('edit/measure/<int:measure_id>/', views.edit_measure, name='edit_measure'),
    path('fokus/', views.edit_goal, name='edit_goal'),
    path('edit/niva/', views.edit_level, name='edit_level'),
    path('edit/omrade', views.edit_omrade, name='edit_omrade'),
    path('edit/tider', views.edit_times, name='edit_times'),
    # Remove things
    path('tabort/kriteria/<int:criteria_id>/', views.delete_criteria, name='delete_criteria'),
    path('tabort/event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('tabort/plats/<int:object_id>/', views.delete_object, name='delete_object'),
    path('tabort/measure/<int:measure_id>/', views.delete_measure, name='delete_measure'),
    path('tabort/pathway/<int:pathway_id>/', views.delete_pathway, name='delete_pathway'),
    #
    path('connect/<int:measure_id>/<int:object_id>/', views.connect_measure, name='connect_measure'),
    path('remove/<int:measure_id>/<int:object_id>/', views.remove_measure, name='remove_measure'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
