
from decimal import Decimal

import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

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

logger = logging.getLogger(__name__)


def send_email_verification(user, request):
	uid = urlsafe_base64_encode(force_bytes(user.pk))
	token = default_token_generator.make_token(user)
	verification_url = request.build_absolute_uri(
		reverse('verify_email', args=[uid, token])
	)
	organization_name = getattr(settings, 'ORG_DISPLAY_NAME', '3rd Gen Loan')
	banner_url = getattr(settings, 'INVITE_BANNER_URL', None) or request.build_absolute_uri(static('email_banner.jpg'))
	context = {
		'user': user,
		'verification_url': verification_url,
		'organization_name': organization_name,
		'banner_url': banner_url,
	}
	subject = f'Confirm your email for {organization_name}'
	text_body = render_to_string('email/verify_email.txt', context)
	html_body = render_to_string('email/verify_email.html', context)
	email = EmailMultiAlternatives(
		subject,
		text_body,
		getattr(settings, 'DEFAULT_FROM_EMAIL', None) or user.email,
		[user.email],
	)
	email.attach_alternative(html_body, 'text/html')
	try:
		email.send(fail_silently=False)
	except (SMTPException, OSError) as exc:
		logger.exception('Verification email failed: %s', exc)
		return False
	return True

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
			user = form.save(commit=False)
			user.is_active = False
			user.email_verified = False
			user.email_verified_at = None
			user.save()
			if send_email_verification(user, request):
				return render(request, 'loan/verify_email_sent.html', {'email': user.email})
			messages.error(
				request,
				"We couldn't send the verification email. Please try again or contact support.",
			)
	else:
		form = UserRegistrationForm()
	return render(request, 'loan/register.html', {'form': form})


def verify_email(request, uidb64, token):
	UserModel = get_user_model()
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = UserModel.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
		user = None
	if user and default_token_generator.check_token(user, token):
		if not user.email_verified:
			user.email_verified = True
			user.email_verified_at = timezone.now()
			user.is_active = True
			user.save(update_fields=['email_verified', 'email_verified_at', 'is_active'])
		messages.success(request, 'Email verified. You can now sign in.')
		return redirect('login')
	messages.error(request, 'Verification link is invalid or has expired. Please request a new link or register again.')
	return redirect('register')

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
			organization_name = getattr(settings, 'ORG_DISPLAY_NAME', '3rdgenloan')
			default_inviter = getattr(settings, 'INVITE_SENDER_NAME', organization_name)
			inviter_name = form.cleaned_data['inviter_name'].strip() or default_inviter
			from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', request.user.email)
			banner_url = getattr(settings, 'INVITE_BANNER_URL', None) or request.build_absolute_uri(static('email_banner.jpg'))
			context = {
				'inviter_name': inviter_name,
				'recipient_name': recipient_name,
				'personalized_note': note,
				'register_url': register_url,
				'organization_name': organization_name,
				'banner_url': banner_url,
			}
			subject = f"{organization_name} invited you to apply for financing"
			text_body = render_to_string('email/register_invite.txt', context)
			html_body = render_to_string('email/register_invite.html', context)
			email = EmailMultiAlternatives(subject, text_body, from_email, [recipient_email])
			email.attach_alternative(html_body, 'text/html')
			try:
				email.send(fail_silently=False)
			except (SMTPException, OSError) as exc:
				logger.exception('Invite email failed: %s', exc)
				console_backend_path = 'django.core.mail.backends.console.EmailBackend'
				if settings.DEBUG:
					active_backend = getattr(settings, 'EMAIL_BACKEND', '')
					if active_backend != console_backend_path:
						logger.info('Falling back to console email backend for invite preview.')
						try:
							email.connection = get_connection(console_backend_path)
							email.send(fail_silently=False)
						except Exception as console_exc:
							logger.exception('Console email fallback failed: %s', console_exc)
						else:
							messages.warning(
								request,
								"SMTP is unreachable, so the invite was dumped to the Django console output instead.",
							)
							return redirect('send_invite')
				messages.error(
					request,
					"We couldn't reach the email server. Please verify SMTP settings or try again later.",
				)
			else:
				messages.success(request, f'Invite sent to {recipient_email}.')
				return redirect('send_invite')
	else:
		form = InviteEmailForm()

	return render(request, 'loan/send_invite.html', {'form': form})
