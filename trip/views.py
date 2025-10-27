# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Destination, Trip, Transportation
from .forms import DestinationForm, ItineraryForm

def home(request):
    trips = Trip.objects.prefetch_related('destination_trips').all()

    context = {
        'trips': trips,
    }  # Adicione esta linha
    return render(request, 'trip/base.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    trips = Trip.objects.filter(user=request.user).order_by('-start_date')
    if trips.exists():
        df = pd.DataFrame(list(trips.values('id', 'start_date', 'end_date', 'budget', 'status')))
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        df['duration'] = (df['end_date'] - df['start_date']).dt.days
        avg_duration = df['duration'].mean()
        avg_budget = df['budget'].mean() if not df['budget'].isna().all() else 0
        status_counts = df['status'].value_counts().to_dict()

        if len(df) > 1:
            plt.figure(figsize=(8, 4))
            df['duration'].plot(kind='bar')
            plt.title('Duração de Viagens')
            plt.tight_layout()
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            duration_chart = f"data:image/png;base64,{img_str}"
        else:
            duration_chart = None
    else:
        avg_duration = 0
        avg_budget = 0
        status_counts = {}
        duration_chart = None

    return render(request, 'trip/dashboard.html', {
        'trips': trips,
        'avg_duration': avg_duration,
        'avg_budget': avg_budget,
        'status_counts': status_counts,
        'duration_chart': duration_chart,
    })

# views.py - Função destination_list corrigida

def destination_list(request):
    from .models import Trip, Destination  # Certifique-se de importar os modelos
    
    search = request.GET.get('search', '')
    order_by = request.GET.get('order_by', 'name')
    direction = request.GET.get('direction', 'asc')
    
    # Query base
    destinations = Destination.objects.all()
    
    # Filtro de busca
    if search:
        destinations = destinations.filter(name__icontains=search)
    
    # Ordenação
    if direction == 'desc':
        order_by = f'-{order_by}'
    
    destinations = destinations.order_by(order_by)
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(destinations, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Buscar todas as viagens para o select
    trips = Trip.objects.all().order_by('name')
    
    context = {
        'db': page_obj,
        'trips': trips,  # Adicionar as viagens no contexto
        'search': search,
        'order_by': request.GET.get('order_by', 'name'),
        'direction': direction,
    }
    
    return render(request, 'trip/destination_list.html', context)

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Destination
from .forms import DestinationForm
from trip.models import Trip  # ajuste conforme necessário

@require_http_methods(["POST"])
def destination_create_update(request):
    """
    View para criar ou atualizar destino
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    destination_id = request.POST.get('destination_id')
    
    if destination_id:
        destination = get_object_or_404(Destination, id=destination_id)
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        action = 'atualizado'
    else:
        form = DestinationForm(request.POST, request.FILES)
        action = 'criado'

    if form.is_valid():
        try:
            destination = form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'message': f'Destino {action} com sucesso!', 'id': destination.id})
            messages.success(request, f'Destino {action} com sucesso!')
            return redirect('trip:destination_list')
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Erro ao salvar: {e}')
    else:
        if is_ajax:
            print("Erros no formulário:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

    # Para requisição não-AJAX com erro, recarrega a página com contexto
    destinations = Destination.objects.all().order_by('-created_at')
    trips = Trip.objects.all().order_by('name')
    
    context = {
        'destinations': destinations,
        'form': form,
        'trips': trips,
        'editing_destination_id': destination_id,
    }
    
    return render(request, 'trip/destination_list.html', context)


def destination_detail(request, destination_id):
    """
    View para retornar dados do destino em JSON (para AJAX)
    """
    destination = get_object_or_404(Destination, id=destination_id)
    
    data = {
        'id': destination.id,
        'name': destination.name,
        'city': destination.city,
        'country': destination.country,
        'slug': destination.slug,
        'arrival_date': destination.arrival_date.strftime('%Y-%m-%d') if destination.arrival_date else '',
        'departure_date': destination.departure_date.strftime('%Y-%m-%d') if destination.departure_date else '',
        'longitude': float(destination.longitude) if destination.longitude else '',
        'latitude': float(destination.latitude) if destination.latitude else '',
        'trip_id': destination.trip.id if destination.trip else '',
        'image': destination.image.url if destination.image else '',
        'description': destination.description,
    }
    print(f"Dados da atualização {data}")
    return JsonResponse(data)

@require_http_methods(["POST"])
def destination_delete(request, destination_id):
    """
    View para deletar destino
    """
    destination = get_object_or_404(Destination, id=destination_id)
    destination_name = destination.name
    destination.delete()
    
    messages.success(request, f'Destino "{destination_name}" removido com sucesso!')
    return redirect('trip:destination_list')

def destination_form(request, slug=None):
    """
    Formulário para criar/editar destino
    """
    if slug:
        destino, created = Destination.objects.get_or_create(slug=slug)
    else:
        destino = None

    if request.method == 'POST':
        form = DestinationForm(request.POST, instance=destino)
        if form.is_valid():
            form.save()
            return redirect('destination_list')
    else:
        form = DestinationForm(instance=destino)

    return render(request, 'trip/destination_form.html', {'form': form})

def itinerary_form(request, city_slug):
    """
    Formulário para criar/editar roteiro de uma cidade
    """
    destination = get_object_or_404(Destination, slug=city_slug)
    
    # Verificar se já existe um roteiro para este destino
    try:
        itinerary = destination.itinerary  # Assumindo relação OneToOne
    except:
        itinerary = None
    
    if request.method == 'POST':
        form = ItineraryForm(request.POST, instance=itinerary)
        if form.is_valid():
            itinerary = form.save(commit=False)
            itinerary.destination = destination
            itinerary.save()
            messages.success(request, f'Roteiro para {destination.name} salvo com sucesso!')
            return redirect('trip:city_detail', city_slug=destination.slug)
    else:
        form = ItineraryForm(instance=itinerary)
    
    context = {
        'form': form,
        'destination': destination,
        'itinerary': itinerary,
    }
    return render(request, 'trip/itinerary_form.html', context)

@login_required
def transportation(request):
    transporte = Transportation.objects.all()  # Corrigido: adicionado ()
    
    if transporte.exists():
        # Converter QuerySet para DataFrame
        df = pd.DataFrame(list(transporte.values('id', 'transport_type', 'company', 'duration_hours', 'price_min')))
        
        # Calcular estatísticas (assumindo que você quer médias numéricas)
        duration_avg = df['duration_hours'].mean() if 'duration_hours' in df.columns else 0
        price_avg = df['price_min'].mean() if 'price_min' in df.columns else 0
        
        # Para campos de texto, você pode querer contagens ao invés de médias
        transport_type_counts = df['transport_type'].value_counts() if 'transport_type' in df.columns else {}
        company_counts = df['company'].value_counts() if 'company' in df.columns else {}
        
        # Criar gráfico se houver dados
        duration_chart = None
        if len(df) > 0:
            plt.figure(figsize=(8, 4))
            
            # Gráfico de tipos de transporte (contagem)
            if not transport_type_counts.empty:
                transport_type_counts.plot(kind='bar')
                plt.title('Tipos de Transporte')
                plt.xlabel('Tipo de Transporte')
                plt.ylabel('Quantidade')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                img_str = base64.b64encode(buffer.read()).decode('utf-8')
                plt.close()
                duration_chart = f"data:image/png;base64,{img_str}"
        
        # Preparar dados para o template
        context_data = {
            'transporte': transporte,
            'transport_type_counts': transport_type_counts,
            'company_counts': company_counts,
            'duration_avg': duration_avg,
            'price_avg': price_avg,
            'duration_chart': duration_chart,
        }
        
    else:
        # Caso não existam dados
        context_data = {
            'transporte': transporte,
            'transport_type_counts': {},
            'company_counts': {},
            'duration_avg': 0,
            'price_avg': 0,
            'duration_chart': None,
        }
    
    return render(request, 'trip/transportation.html', context_data)

def city_detail(request, city_slug):
    """
    Detalhes de uma cidade específica
    """
    destination = get_object_or_404(Destination, slug=city_slug)
    context = {
        'destination': destination,
    }
    return render(request, 'trip/city_detail.html', context)
