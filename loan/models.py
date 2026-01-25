
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Audit log model
class AuditLog(models.Model):
	admin = models.ForeignKey('User', on_delete=models.CASCADE, related_name='admin_logs')
	action = models.CharField(max_length=100)
	entity_type = models.CharField(max_length=100)
	entity_id = models.PositiveIntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.admin.email} {self.action} {self.entity_type} {self.entity_id} at {self.timestamp}"

# Loan model
class Loan(models.Model):
	STATUS_CHOICES = [
		("PENDING", "Pending"),
		("APPROVED", "Approved"),
		("ACTIVE", "Active"),
		("CLOSED", "Closed"),
		("REJECTED", "Rejected"),
	]
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='loans')
	requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
	approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
	term_months = models.PositiveIntegerField()
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
	loan_purpose = models.CharField(max_length=255)
	monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
	note = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	approved_at = models.DateTimeField(null=True, blank=True)
	closed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"Loan {self.id} for {self.user.email} ({self.status})"


class WithdrawalRequest(models.Model):
	STATUS_CHOICES = [
		("PENDING", "Pending"),
		("APPROVED", "Approved"),
		("REJECTED", "Rejected"),
	]
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='withdrawal_requests')
	loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='withdrawal_requests')
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
	note = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	processed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"Withdrawal {self.id} for Loan {self.loan_id} ({self.status})"
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
	def create_user(self, email, phone, full_name, password=None, role='USER', **extra_fields):
		if not email:
			raise ValueError('Users must have an email address')
		if not phone:
			raise ValueError('Users must have a phone number')
		email = self.normalize_email(email)
		user = self.model(email=email, phone=phone, full_name=full_name, role=role, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, phone, full_name, password=None, **extra_fields):
		extra_fields.setdefault('role', 'ADMIN')
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		return self.create_user(email, phone, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	ROLE_CHOICES = (
		('USER', 'User'),
		('ADMIN', 'Admin'),
	)
	full_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20, unique=True)
	password_hash = models.CharField(max_length=128)
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	email_verified = models.BooleanField(default=False)
	email_verified_at = models.DateTimeField(null=True, blank=True)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['phone', 'full_name']

	def save(self, *args, **kwargs):
		if self.password and not self.password_hash:
			self.set_password(self.password)
		super().save(*args, **kwargs)

	def set_password(self, raw_password):
		super().set_password(raw_password)
		self.password_hash = self.password

	def __str__(self):
		return self.email


# User profile model
class Profile(models.Model):
	MARITAL_STATUS_CHOICES = [
		('SINGLE', 'Single'),
		('MARRIED', 'Married'),
		('PARTNERED', 'Domestic partnership'),
		('DIVORCED', 'Divorced'),
		('WIDOWED', 'Widowed'),
	]

	HOUSING_STATUS_CHOICES = [
		('OWN', 'Own home'),
		('RENT', 'Renting'),
		('FAMILY', 'Living with family'),
		('MILITARY', 'Military housing'),
		('OTHER', 'Other arrangement'),
	]

	user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
	street_address = models.CharField(max_length=255)
	city = models.CharField(max_length=120, blank=True, default='')
	state = models.CharField(max_length=120, blank=True, default='')
	postal_code = models.CharField(max_length=20, blank=True, default='')
	nationality = models.CharField(max_length=120, blank=True, default='')
	marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, default='')
	housing_status = models.CharField(max_length=20, choices=HOUSING_STATUS_CHOICES, blank=True, default='')
	dob = models.DateField(verbose_name='Date of Birth')
	employment_status = models.CharField(max_length=100)
	monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
	completed = models.BooleanField(default=False)
    
	def __str__(self):
		return f"Profile for {self.user.email}"


# Signed agreement record for loans
class LoanAgreement(models.Model):
	loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='agreements')
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='agreements')
	borrower_name = models.CharField(max_length=255)
	requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
	account_last4 = models.CharField(max_length=8, blank=True, default='')
	signature_image = models.ImageField(upload_to='agreements/signatures/', null=True, blank=True)
	signature_text = models.CharField(max_length=255, blank=True)
	signed_at = models.DateTimeField(null=True, blank=True)
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.TextField(blank=True)
	terms_version = models.CharField(max_length=64, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Agreement {self.id} for Loan {self.loan_id} by {self.user.email}"

# Bank details model
class BankDetail(models.Model):
	user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='bank_detail')
	bank_name = models.CharField(max_length=100)
	account_name = models.CharField(max_length=100)
	account_number = models.CharField(max_length=64)  # Placeholder for encrypted field
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Bank details for {self.user.email}"
