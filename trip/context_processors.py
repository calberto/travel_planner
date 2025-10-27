# trip/context_processors.py
from .models import Destination

def destinations_menu(request):
    """
    Context processor para disponibilizar destinos no menu
    """
    destinations = Destination.objects.all().order_by('country', 'name')
    return {
        'destinations': destinations
    }
