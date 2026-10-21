from django.conf import settings
from django.db import models


class AccountProfile(models.Model):
    """LifeLink account fields that extend Django's built-in user."""

    class Role(models.TextChoices):
        REQUESTER = 'requester', 'Requester'
        DONOR = 'donor', 'Donor'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='account_profile',
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    role = models.CharField(max_length=20, choices=Role.choices)
    account_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} ({self.role})'


class BloodType(models.Model):
    code = models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


class Barangay(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='Quezon City')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'city'], name='unique_barangay_per_city'),
        ]

    def __str__(self):
        return f'{self.name}, {self.city}'


class RequesterProfile(models.Model):
    class RequesterType(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        REPRESENTATIVE = 'representative', 'Representative'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='requester_profile',
    )
    requester_type = models.CharField(max_length=20, choices=RequesterType.choices)
    relationship_to_patient = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'Requester profile for user {self.user_id}'


class DonorProfile(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        UNAVAILABLE = 'unavailable', 'Unavailable'

    class Eligibility(models.TextChoices):
        ELIGIBLE = 'eligible', 'Eligible by donation interval'
        COOLDOWN = 'cooldown', 'In donation cooldown'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='donor_profile',
    )
    blood_type = models.ForeignKey(BloodType, on_delete=models.PROTECT, related_name='donors')
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name='donors')
    availability_status = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    eligibility_status = models.CharField(max_length=20, choices=Eligibility.choices)
    last_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Donor profile for user {self.user_id}'
