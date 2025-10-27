# Formulários Django
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import DateInput, TimeInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Div
from .models import Trip,Destination, Itinerary, ItineraryActivity, City, Country

class DestinationForm(forms.ModelForm):
    """
    Formulário para criar/editar destinos
    """
    
    class Meta:
        model = Destination
        fields = [
            'name', 'city', 'country', 'slug', 'trip', 
            'arrival_date', 'departure_date', 'longitude', 
            'latitude', 'image', 'description'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets e atributos
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome do destino',
            'required': True
        })
        
        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Cidade'
        })
        
        self.fields['country'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'País'
        })
        
        self.fields['slug'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'URL amigável (opcional)'
        })
        
        self.fields['trip'].widget.attrs.update({
            'class': 'form-control'
        })
        
        self.fields['arrival_date'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
        
        self.fields['departure_date'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
        
        self.fields['longitude'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Longitude (ex: -23.5505)',
            'step': 'any'
        })
        
        self.fields['latitude'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Latitude (ex: -46.6333)',
            'step': 'any'
        })
        
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        
        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Descrição do destino',
            'rows': 3
        })
        
        # Tornar campos opcionais
        self.fields['slug'].required = False
        self.fields['trip'].required = False
        self.fields['arrival_date'].required = False
        self.fields['departure_date'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].required = False
        self.fields['image'].required = False
        self.fields['description'].required = False
        
        # Definir queryset para trips
        self.fields['trip'].queryset = Trip.objects.all().order_by('name')
        self.fields['trip'].empty_label = "Selecione uma viagem"
    
    def clean_slug(self):
        """
        Validar slug único
        """
        slug = self.cleaned_data.get('slug')
        if slug:
            # Verificar se já existe outro destino com o mesmo slug
            existing = Destination.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError("Este slug já está em uso.")
        
        return slug
    
    def clean(self):
        """
        Validações gerais do formulário
        """
        cleaned_data = super().clean()
        arrival_date = cleaned_data.get('arrival_date')
        departure_date = cleaned_data.get('departure_date')

        if arrival_date and departure_date and departure_date < arrival_date:
            raise forms.ValidationError("A data de partida não pode ser anterior à data de chegada.")
        
        return cleaned_data

class TripForm(forms.ModelForm):
    """Formulário para criar/editar uma viagem"""
    class Meta:
        model = Trip
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            Row(
                Column('start_date', css_class='form-group col-md-6'),
                Column('end_date', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('status', css_class='form-group col-md-6'),
                Column('budget', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'notes',
            Div(
                Submit('submit', 'Salvar', css_class='btn-primary'),
                HTML('<a href="{% url "dashboard" %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-3'
            )
        )
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise ValidationError('A data de término deve ser após a data de início')
        return cleaned_data


class ItineraryForm(forms.ModelForm):
    cities = forms.ModelMultipleChoiceField(
        queryset=City.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Itinerary
        fields = ['title', 'description', 'cities', 'start_date', 'end_date', 
                 'budget', 'status', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Data de início deve ser anterior à data de fim.")
        
        return cleaned_data

class ItineraryActivityForm(forms.ModelForm):
    class Meta:
        model = ItineraryActivity
        fields = ['activity', 'day_number', 'start_time', 'end_time', 'notes', 'order']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

"""
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'category', 'city', 'address', 
                 'price', 'duration_hours', 'rating']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'duration_hours': forms.NumberInput(attrs={'step': '0.5'}),
            'rating': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '5'}),
        }


class CitySearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o nome da cidade...',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )


class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = ['city', 'name', 'Accommodation_type', 'area', 'price_per_night', 
                  'rating', 'booking_url']
        
    def __init__(self, *args, **kwargs):
        super(AccommodationForm, self).__init__(*args, **kwargs)
        # Definindo labels em português
        self.fields['city'].label = "Cidade"
        self.fields['name'].label = "Nome da Acomodação"
        self.fields['Accommodation_type'].label = "Tipo de Acomodação"
        self.fields['area'].label = "Área"
        self.fields['price_per_night'].label = "Preço por noite"
        self.fields['rating'].label = "Classificação"
        self.fields['booking_url'].label = "Endereço Eletrônico"
        
        # Opcional: Adicionar widgets para melhorar a experiência do usuário
        self.fields['price_per_night'].widget.attrs.update({'step': '0.01'})
        self.fields['rating'].widget.attrs.update({'step': '0.1', 'min': '0', 'max': '5'})





class TripCityForm(forms.ModelForm):
    Formulário para adicionar uma cidade ao itinerário

    class Meta:
        model = TripCity
        fields = ['city', 'arrival_date', 'departure_date', 'accommodation', 'transport_to_next', 'notes']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }                  

        def __init__(self, *args, **kwargs):
            trip = kwargs.pop('trip', None)
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            
            # Se trip foi fornecido, filtre campos baseados nele
            if trip:
                self.trip = trip
                # Limitar opções de acomodação apenas para a cidade selecionada
                self.fields['accommodation'].queryset = Accommodation.objects.none()
                
                # Data de chegada não pode ser antes do início da viagem
                self.fields['arrival_date'].widget.attrs['min'] = trip.start_date
                
                # Data de saída não pode ser depois do fim da viagem
                self.fields['departure_date'].widget.attrs['max'] = trip.end_date
            
                self.helper.layout = Layout(
                'city',
                Row(
                    Column('arrival_date', css_class='form-group col-md-6'),
                    Column('departure_date', css_class='form-group col-md-6'),
                    css_class='form-row'
                ),
                'accommodation',
                'transport_to_next',
                'notes',
                Div(
                    Submit('submit', 'Adicionar ao Itinerário', css_class='btn-primary'),
                    HTML('<a href="{{ trip_detail_url }}" class="btn btn-secondary ms-2">Cancelar</a>'),
                    css_class='mt-3'
                )
            )
    
    def clean(self):
        cleaned_data = super().clean()
        arrival_date = cleaned_data.get('arrival_date')
        departure_date = cleaned_data.get('departure_date')
        city = cleaned_data.get('city')
        
        if arrival_date and departure_date and departure_date < arrival_date:
            raise ValidationError('A data de saída deve ser após ou igual à data de chegada.')
        
        # Verificar se há conflitos com outras cidades no itinerário
        if hasattr(self, 'trip') and arrival_date and departure_date:
            overlapping = self.trip.trip_cities.filter(
                arrival_date__lte=departure_date,
                departure_date__gte=arrival_date
            ).exists()
            
            if overlapping:
                raise ValidationError('Há sobreposição de datas com outra cidade no itinerário.')
        
        # Se cidade e datas válidas, atualize as opções de acomodação
        if city and not self._errors.get('city'):
            self.fields['accommodation'].queryset = Accommodation.objects.filter(city=city)
        
        return cleaned_data
    
class LearningEntryForm(forms.ModelForm):
    Formulário para adicionar uma entrada de aprendizagem
    
    class Meta:
        model = LearningEntry
        fields = ['city', 'entry_type', 'title', 'content', 'entry_date']
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            Row(
                Column('entry_type', css_class='form-group col-md-6'),
                Column('city', css_class='form-group col-md-6'),
                css_class='form-row'
            )
        )     
"""