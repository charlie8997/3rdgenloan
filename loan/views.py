
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse

from .forms import (
	LoanForm,
	ProfileForm,
	UserRegistrationForm,
	UserLoginForm,
	BankDetailForm,
	WithdrawalRequestForm,
	InviteEmailForm,
)
from .models import Loan, BankDetail, Profile, User, WithdrawalRequest

@login_required
def loan_dashboard(request):
	loan = Loan.objects.filter(user=request.user).order_by('-created_at').first()
	balance = None
	approved_withdrawals_total = Decimal('0.00')
	available_balance = None
	withdrawal_requests = []
	if loan and loan.status in ["APPROVED", "ACTIVE"]:
		approved_amount = loan.approved_amount or loan.requested_amount
		approved_withdrawals_total = WithdrawalRequest.objects.filter(
			loan=loan, status="APPROVED"
		).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
		available_balance = approved_amount - approved_withdrawals_total
		balance = available_balance
		withdrawal_requests = WithdrawalRequest.objects.filter(loan=loan).order_by('-created_at')
	return render(
		request,
		'loan/loan_dashboard.html',
		{
			'loan': loan,
			'balance': balance,
			'available_balance': available_balance,
			'approved_withdrawals_total': approved_withdrawals_total,
			'withdrawal_requests': withdrawal_requests,
		},
	)

@login_required
def loan_application(request):
	# Preconditions: profile and bank details completed, no active/pending loan
	if not (hasattr(request.user, 'profile') and request.user.profile.completed):
		return redirect('profile_complete')
	if not hasattr(request.user, 'bank_detail'):
		return redirect('bank_detail')
	has_pending_or_active = Loan.objects.filter(user=request.user, status__in=["PENDING", "APPROVED", "ACTIVE"]).exists()
	if has_pending_or_active:
		return render(request, 'loan/loan_already_exists.html')
	if request.method == 'POST':
		form = LoanForm(request.POST)
		if form.is_valid():
			loan = form.save(commit=False)
			loan.user = request.user
			loan.status = "PENDING"
			loan.save()
			return redirect('loan_dashboard')
	else:
		form = LoanForm()
	return render(request, 'loan/loan_application.html', {'form': form})

def register(request):
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('profile_complete')
	else:
		form = UserRegistrationForm()
	return render(request, 'loan/register.html', {'form': form})

def user_login(request):
	if request.method == 'POST':
		form = UserLoginForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('loan_dashboard')
		else:
			# Check if user exists
			from django.contrib.auth import get_user_model
			User = get_user_model()
			email = request.POST.get('username')
			if not User.objects.filter(email=email).exists():
				from django.contrib import messages
				messages.error(request, 'No account found with this email address.')
	else:
		form = UserLoginForm()
	return render(request, 'loan/login.html', {'form': form})

def user_logout(request):
	logout(request)
	return redirect('login')

@login_required
def profile_complete(request):
	try:
		profile = request.user.profile
	except Profile.DoesNotExist:
		profile = None
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=profile)
		if form.is_valid():
			profile = form.save(commit=False)
			profile.user = request.user
			profile.completed = True
			profile.save()
			return redirect('bank_detail')
	else:
		form = ProfileForm(instance=profile)
	return render(request, 'loan/profile_complete.html', {'form': form})

@login_required
def bank_detail(request):
	try:
		bank_detail = request.user.bank_detail
	except BankDetail.DoesNotExist:
		bank_detail = None
	if request.method == 'POST':
		form = BankDetailForm(request.POST, instance=bank_detail)
		if form.is_valid():
			bank_detail = form.save(commit=False)
			bank_detail.user = request.user
			bank_detail.save()
			return redirect('loan_dashboard')
	else:
		form = BankDetailForm(instance=bank_detail)
	return render(request, 'loan/bank_detail.html', {'form': form})

@login_required
def withdrawal_request(request):
	loan = Loan.objects.filter(user=request.user).order_by('-created_at').first()
	if not loan or loan.status not in ["APPROVED", "ACTIVE"]:
		return redirect('loan_dashboard')

	approved_amount = loan.approved_amount or loan.requested_amount
	approved_withdrawals_total = WithdrawalRequest.objects.filter(
		loan=loan, status="APPROVED"
	).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
	available_balance = approved_amount - approved_withdrawals_total

	if request.method == 'POST':
		form = WithdrawalRequestForm(request.POST)
		if form.is_valid():
			withdrawal = form.save(commit=False)
			if withdrawal.amount <= 0:
				form.add_error('amount', 'Amount must be greater than zero.')
			elif withdrawal.amount > available_balance:
				form.add_error('amount', 'Amount exceeds available balance.')
			else:
				withdrawal.user = request.user
				withdrawal.loan = loan
				withdrawal.status = "PENDING"
				withdrawal.save()
				return redirect('loan_dashboard')
	else:
		form = WithdrawalRequestForm()

	return render(
		request,
		'loan/withdrawal_request.html',
		{
			'form': form,
			'loan': loan,
			'available_balance': available_balance,
			'approved_amount': approved_amount,
			'approved_withdrawals_total': approved_withdrawals_total,
		},
	)


@login_required
def send_invite(request):
	if not request.user.is_staff:
		raise PermissionDenied('Only administrators can send invitations.')

	if request.method == 'POST':
		form = InviteEmailForm(request.POST)
		if form.is_valid():
			recipient_name = form.cleaned_data['recipient_name']
			recipient_email = form.cleaned_data['recipient_email']
			note = form.cleaned_data['personalized_note']
			register_url = request.build_absolute_uri(reverse('register'))
			inviter_name = getattr(request.user, 'full_name', '') or request.user.email
			from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', request.user.email)
			banner_url = getattr(settings, 'INVITE_BANNER_URL', None) or request.build_absolute_uri(static('email_banner.jpg'))
			organization_name = getattr(settings, 'ORG_DISPLAY_NAME', 'Loan System')
			context = {
				'inviter_name': inviter_name,
				'recipient_name': recipient_name,
				'personalized_note': note,
				'register_url': register_url,
				'organization_name': organization_name,
				'banner_url': banner_url,
			}
			subject = f"{inviter_name} invited you to apply for financing"
			text_body = render_to_string('email/register_invite.txt', context)
			html_body = render_to_string('email/register_invite.html', context)
			email = EmailMultiAlternatives(subject, text_body, from_email, [recipient_email])
			email.attach_alternative(html_body, 'text/html')
			email.send(fail_silently=False)
			messages.success(request, f'Invite sent to {recipient_email}.')
			return redirect('send_invite')
	else:
		form = InviteEmailForm()

	return render(request, 'loan/send_invite.html', {'form': form})
