from django import forms

from .models import Listing, Message


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'price', 'condition', 'location', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False
        self.fields['status'].initial = Listing.Status.ACTIVE
        self.fields['status'].choices = [
            (Listing.Status.DRAFT, 'Draft'),
            (Listing.Status.ACTIVE, 'Active'),
            (Listing.Status.SOLD, 'Sold'),
            (Listing.Status.ARCHIVED, 'Archived'),
        ]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ask the seller about this listing...',
            }),
        }
