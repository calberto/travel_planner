from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Trip, Destination

@login_required
def destination_list(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if trip.user != request.user:
        return redirect('trip:trip_list')
    destinations = Destination.objects.filter(trip_id=trip_id)
    return render(request, 'trip/destinations_list.html', {
        'destinations': destinations,
        'trip_id': trip_id,
        'trip': trip,
    })