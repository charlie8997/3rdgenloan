from django import forms
from django.conf import settings


class InviteWhatsAppForm(forms.Form):
    inviter_name = forms.CharField(
        label='Sender name',
        max_length=120,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '3rd Gen Loan team'
        })
    )
    recipient_name = forms.CharField(
        label='Recipient name',
        max_length=120,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Jane Borrower'
        })
    )
    recipient_email = forms.EmailField(
        label='Recipient email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'jane@example.com'
        })
    )
    whatsapp_url = forms.URLField(
        label='WhatsApp / contact URL',
        required=True,
        widget=forms.URLInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'https://wa.me/15551234567 or https://app.example.com/update-contact'
        })
    )
    personalized_note = forms.CharField(
        label='Personal note',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Optional message that will appear in the email body.',
            'rows': 3
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_sender = getattr(
            settings,
            'INVITE_SENDER_NAME',
            getattr(settings, 'ORG_DISPLAY_NAME', 'Loan System'),
        )
        if default_sender:
            self.fields['inviter_name'].initial = default_sender
