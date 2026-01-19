from django.contrib import admin
from django.utils import timezone
from .models import User, Profile, BankDetail, Loan, AuditLog, WithdrawalRequest
from django.contrib import messages

def approve_loan(modeladmin, request, queryset):
	for loan in queryset:
		if loan.status == 'PENDING':
			loan.status = 'APPROVED'
			if not loan.approved_amount:
				loan.approved_amount = loan.requested_amount
			loan.save()
			AuditLog.objects.create(
				admin=request.user,
				action='APPROVED',
				entity_type='Loan',
				entity_id=loan.id
			)
			messages.success(request, f"Loan {loan.id} approved.")
approve_loan.short_description = "Approve selected loans"

def reject_loan(modeladmin, request, queryset):
	for loan in queryset:
		if loan.status == 'PENDING':
			loan.status = 'REJECTED'
			loan.save()
			AuditLog.objects.create(
				admin=request.user,
				action='REJECTED',
				entity_type='Loan',
				entity_id=loan.id
			)
			messages.success(request, f"Loan {loan.id} rejected.")
reject_loan.short_description = "Reject selected loans"

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'requested_amount', 'approved_amount', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	actions = [approve_loan, reject_loan]

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ('admin', 'action', 'entity_type', 'entity_id', 'timestamp')
	list_filter = ('action', 'entity_type', 'timestamp')

def approve_withdrawal(modeladmin, request, queryset):
	for withdrawal in queryset:
		if withdrawal.status == 'PENDING':
			withdrawal.status = 'APPROVED'
			withdrawal.processed_at = timezone.now()
			withdrawal.save()
			AuditLog.objects.create(
				admin=request.user,
				action='APPROVED_WITHDRAWAL',
				entity_type='WithdrawalRequest',
				entity_id=withdrawal.id
			)
			messages.success(request, f"Withdrawal {withdrawal.id} approved.")
approve_withdrawal.short_description = "Approve selected withdrawals"

def reject_withdrawal(modeladmin, request, queryset):
	for withdrawal in queryset:
		if withdrawal.status == 'PENDING':
			withdrawal.status = 'REJECTED'
			withdrawal.processed_at = timezone.now()
			withdrawal.save()
			AuditLog.objects.create(
				admin=request.user,
				action='REJECTED_WITHDRAWAL',
				entity_type='WithdrawalRequest',
				entity_id=withdrawal.id
			)
			messages.success(request, f"Withdrawal {withdrawal.id} rejected.")
reject_withdrawal.short_description = "Reject selected withdrawals"

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'loan', 'amount', 'status', 'created_at', 'processed_at')
	list_filter = ('status', 'created_at')
	actions = [approve_withdrawal, reject_withdrawal]

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(BankDetail)
