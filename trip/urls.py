from django.urls import path
from . import views

app_name = 'trip'

urlpatterns = [
    # Página inicial do aplicativo de viagens
    path('', views.home, name='home'),

    # Página do dashboard da aplicação
    path('trips/dashboard/', views.dashboard, name='dashboard'),

    path('trips/destinations/', views.destination_list, name='destination_list'),
    path('destinations/detail/<int:destination_id>/', views.destination_detail, name='destination_detail'),
    path('destination/create_update/', views.destination_create_update, name='destination_create_update'),
    path('destination/<slug:slug>/edit/', views.destination_form, name='destination_form'),
    path('destinations/delete/<int:destination_id>/', views.destination_delete, name='destination_delete'),
    path('destination/<slug:slug>/', views.city_detail, name='city_detail'),
    # Logout
    path('logout/', views.logout_view, name='logout'),
    # Página do transporte da aplicação
    path('trips/transportation/', views.transportation, name='transportation'),

    path('itinerary/<slug:city_slug>/form/', views.itinerary_form, name='itinerary_form'),

]    
    
"""
    # Página do acomodação da aplicação
    path('trips/accommodation/', views.accommodation, name='accommodation'),

    # Listar todas as viagens
    path('trips/', views.trip_list, name='trip_list'),

    # Criar uma nova viagem
    path('trips/new/', views.trip_create, name='trip_create'),
    
    # Detalhe de uma viagem específica
    path('trips/<int:trip_id>/', views.trip_detail, name='trip_detail'),

    # Editar uma viagem existente
    path('trip/edit/<int:trip_id>/', views.trip_edit, name='trip_edit'),
    path('trips/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    
    # Excluir uma viagem
    path('trips/<int:trip_id>/delete/', views.trip_delete, name='trip_delete'),

    # Adicionar um destino a uma viagem
    path('trips/<int:trip_id>/add-destination/', views.add_destination, name='add_destination'),

    # CORREÇÃO: URLs para atividades
    path('trip/destination/<int:destination_id>/add-activity/', views.add_activity, name='add_activity'),
    path('trips/activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('trips/activities/create/', views.activity_create, name='activity_create'),
    path('trips/activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    
    # CORREÇÃO: URLs para Itinerary (removido o '?')
    path('trips/itineraries/', views.itinerary_list, name='itinerary_list'),
    path('trips/itineraries/<int:pk>/', views.itinerary_detail, name='itinerary_detail'),
    path('trips/itineraries/create/', views.itinerary_create, name='itinerary_create'),
    path('trips/itineraries/<int:pk>/edit/', views.itinerary_edit, name='itinerary_edit'),
    path('trips/itineraries/<int:itinerary_pk>/add-activity/', views.add_activity_to_itinerary, name='add_activity_to_itinerary'),
    
    # Pesquisar destinos
    path('search/', views.search_destinations, name='search_destinations'),

    # Perfil do usuário
    path('profile/', views.user_profile, name='user_profile'),

    # API para autocompletar cidades
    path('api/cities/autocomplete/', views.city_autocomplete, name='city_autocomplete'),
    path('city/<int:city_id>/transport/', views.city_transport, name='city_transport'),
   
   
"""
   
    

