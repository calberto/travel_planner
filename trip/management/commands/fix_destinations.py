from django.core.management.base import BaseCommand
from trip.models import Trip, Destination

class Command(BaseCommand):
    help = 'Corrigir destinos vazios nas viagens existentes'

    def handle(self, *args, **options):
        self.stdout.write('Verificando viagens com destinos vazios...')
        
        # Buscar viagens sem destino
        trips_without_destination = Trip.objects.filter(
            destination__isnull=True
        ) | Trip.objects.filter(destination='')
        
        self.stdout.write(f'Encontradas {trips_without_destination.count()} viagens sem destino')
        
        if trips_without_destination.count() == 0:
            self.stdout.write(self.style.SUCCESS('Todas as viagens já têm destino!'))
            return
        
        for trip in trips_without_destination:
            self.stdout.write(f'\nViagem: {trip.title}')
            self.stdout.write(f'ID: {trip.id}')
            self.stdout.write(f'Data: {trip.start_date}')
            
            # Você pode definir um destino padrão baseado no título ou pedir input
            # Por exemplo, tentar extrair do título:
            if hasattr(trip, 'title') and trip.title:
                # Tentar extrair destino do título
                possible_destination = self.extract_destination_from_title(trip.title)
                if possible_destination:
                    trip.destination = possible_destination
                    trip.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Destino definido como: {possible_destination}')
                    )
                else:
                    # Definir destino genérico
                    trip.destination = "Destino não especificado"
                    trip.save()
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Destino definido como: Destino não especificado')
                    )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Correção concluída!'))
        
        # Agora popular a tabela de destinos
        self.stdout.write('\nPopulando tabela de destinos...')
        unique_destinations = Trip.objects.values_list('destination', flat=True).distinct()
        
        created_count = 0
        for dest_name in unique_destinations:
            if dest_name and dest_name.strip():
                trip_count = Trip.objects.filter(destination=dest_name).count()
                destination, created = Destination.objects.get_or_create(
                    name=dest_name.strip(),
                    defaults={
                        'description': f'Destino com {trip_count} viagem{"s" if trip_count != 1 else ""}'
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'✓ Destino criado: {dest_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Criados {created_count} destinos!'))
    
    def extract_destination_from_title(self, title):
        """Tentar extrair destino do título da viagem"""
        # Palavras comuns que podem indicar destinos
        common_destinations = [
            'Rio de Janeiro', 'São Paulo', 'Salvador', 'Recife', 'Fortaleza',
            'Brasília', 'Belo Horizonte', 'Curitiba', 'Porto Alegre', 'Manaus',
            'Belém', 'Goiânia', 'Campinas', 'Florianópolis', 'Natal',
            'Paris', 'Londres', 'Nova York', 'Tokyo', 'Lisboa', 'Madrid'
        ]
        
        title_lower = title.lower()
        for dest in common_destinations:
            if dest.lower() in title_lower:
                return dest
        
        # Se não encontrar, retornar None
        return None