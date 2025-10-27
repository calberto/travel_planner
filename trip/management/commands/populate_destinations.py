from django.core.management.base import BaseCommand
from django.db.models import Count
from trip.models import Trip, Destination

class Command(BaseCommand):
    help = 'Popular tabela de destinos baseado nas viagens existentes'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando processo de população de destinos...')
        
        # Debug: verificar quantas viagens existem
        total_trips = Trip.objects.count()
        self.stdout.write(f'Total de viagens na base: {total_trips}')
        
        if total_trips == 0:
            self.stdout.write(
                self.style.WARNING('Nenhuma viagem encontrada! Adicione viagens primeiro.')
            )
            return
        
        # Pegar todos os destinos únicos das viagens
        unique_destinations = Trip.objects.values_list('destination', flat=True).distinct()
        
        self.stdout.write(f'Destinos únicos encontrados: {list(unique_destinations)}')
        self.stdout.write(f'Total de destinos únicos: {len(unique_destinations)}')
        
        if not unique_destinations:
            self.stdout.write(
                self.style.WARNING('Nenhum destino encontrado nas viagens!')
            )
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for dest_name in unique_destinations:
            self.stdout.write(f'Processando destino: "{dest_name}"')
            
            if not dest_name or not dest_name.strip():
                self.stdout.write(f'Pulando destino vazio ou só espaços')
                skipped_count += 1
                continue
            
            # Contar quantas viagens tem esse destino
            trip_count = Trip.objects.filter(destination=dest_name).count()
            self.stdout.write(f'  -> {trip_count} viagens para este destino')
            
            try:
                destination, created = Destination.objects.get_or_create(
                    name=dest_name.strip(),
                    defaults={
                        'description': f'Destino com {trip_count} viagem{"s" if trip_count != 1 else ""}'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ CRIADO: {dest_name} (ID: {destination.id})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(f'• JÁ EXISTE: {dest_name} (ID: {destination.id})')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar/buscar destino "{dest_name}": {e}')
                )
        
        # Verificação final
        total_destinations_after = Destination.objects.count()
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'RESULTADO FINAL:')
        self.stdout.write(f'• {created_count} destinos criados')
        self.stdout.write(f'• {updated_count} destinos já existiam')
        self.stdout.write(f'• {skipped_count} destinos pulados (vazios)')
        self.stdout.write(f'• Total na tabela Destination agora: {total_destinations_after}')
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS('✅ Processo concluído com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Nenhum novo destino foi criado'))