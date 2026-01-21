from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Loan, Profile, User, BankDetail, WithdrawalRequest


class InviteEmailForm(forms.Form):
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


# Loan application form
class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['requested_amount', 'loan_purpose', 'term_months', 'monthly_income', 'note']
        widgets = {
            'requested_amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'How much do you need?'
            }),
            'loan_purpose': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'What will the funds cover?'
            }),
            'term_months': forms.Select(choices=[(i, (f"{i} month" if i == 1 else f"{i} months")) for i in range(1, 13)], attrs={
                'class': 'form-select form-select-lg',
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Monthly income before taxes'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Anything else our underwriting team should know? (optional)',
                'rows': 3
            }),
        }

class ProfileForm(forms.ModelForm):
    EMPLOYMENT_CHOICES = [
        ('FULL_TIME', 'Full-time employed'),
        ('PART_TIME', 'Part-time employed'),
        ('SELF_EMPLOYED', 'Self-employed'),
        ('CONTRACTOR', 'Contractor / Gig worker'),
        ('UNEMPLOYED', 'Currently unemployed'),
        ('RETIRED', 'Retired'),
        ('STUDENT', 'Student'),
    ]

    employment_status = forms.ChoiceField(
        choices=EMPLOYMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = Profile
        fields = [
            'street_address',
            'city',
            'state',
            'postal_code',
            'nationality',
            'marital_status',
            'housing_status',
            'dob',
            'employment_status',
            'monthly_income',
        ]
        widgets = {
            'street_address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Street address, Apt/Suite',
                'id': 'address-input',
                'autocomplete': 'address-line1',
                'spellcheck': 'false'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'City',
                'autocomplete': 'address-level2'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'State / Province',
                'autocomplete': 'address-level1'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Postal / ZIP',
                'autocomplete': 'postal-code'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Country of citizenship'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'housing_status': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'dob': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg',
                'placeholder': 'MM/DD/YYYY'
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Monthly income before taxes',
                'min': 0,
                'step': '0.01',
                'inputmode': 'decimal'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            'street_address',
            'city',
            'state',
            'postal_code',
            'nationality',
            'marital_status',
            'housing_status',
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise ValidationError('Date of birth is required.')
        from datetime import date
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise ValidationError('You must be at least 18 years old to apply.')
        return dob


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Create a secure password'
            }
        )
    )
    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Re-enter password'
            }
        )
    )
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Legal full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'you@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '5551234567',
                'id': 'phone-input'
            }),
        }

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone_raw = self.cleaned_data.get('phone', '').strip()
        if not phone_raw:
            raise ValidationError('Enter a valid mobile number.')
        digits = ''.join(filter(str.isdigit, phone_raw))
        if len(digits) < 10:
            raise ValidationError('Enter a valid mobile number.')
        normalized = '+' + digits
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'you@example.com'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Your password'
        })
    )

    def confirm_login_allowed(self, user):
        if not getattr(user, 'email_verified', False):
            raise ValidationError('Please verify your email before signing in.')
        super().confirm_login_allowed(user)

class BankDetailForm(forms.ModelForm):
    class Meta:
        model = BankDetail
        fields = ['bank_name', 'account_name', 'account_number']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Bank or credit union name'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Name on the account'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Checking account number'
            }),
        }

class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-end border-start-0',
                'placeholder': '0.00',
                'min': 1,
                'step': '0.01',
                'inputmode': 'decimal',
                'id': 'withdraw-amount-input'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Add any context or payout instructions (optional)',
                'rows': 3
            }),
        }
