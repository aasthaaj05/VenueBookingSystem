from django import forms
from gymkhana.models import Venue

class VenueSelectForm(forms.Form):
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        label="Select a venue to edit",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class VenueEditForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = '__all__'
        exclude = ['id', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'venue_location': forms.Textarea(attrs={'rows': 3}),
            'facilities': forms.TextInput(attrs={'placeholder': 'Enter as comma-separated list'}),
            'photo_url': forms.URLInput(attrs={'placeholder': 'Enter full URL'}),
            'picture_urls': forms.URLInput(attrs={'placeholder': 'Enter full URL'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['facilities'].help_text = 'Enter facilities as a JSON array (e.g., ["Projector", "Whiteboard"])'





