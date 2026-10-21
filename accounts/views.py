import json
from calendar import monthrange
from datetime import date

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import (
    AccountProfile,
    Barangay,
    BloodType,
    DonorProfile,
    RequesterProfile,
)


def add_months(day, months):
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(day.day, monthrange(year, month)[1]))


@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    """Create a shared LifeLink account and its initial requester/donor role."""
    if 'application/json' not in request.headers.get('Content-Type', '').lower():
        return JsonResponse(
            {'error': {'code': 'unsupported_media_type', 'message': 'Send the request as application/json.'}},
            status=415,
        )

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'error': {'code': 'invalid_json', 'message': 'Request body must contain valid JSON.'}},
            status=400,
        )
    if not isinstance(payload, dict):
        return JsonResponse(
            {'error': {'code': 'invalid_payload', 'message': 'JSON body must be an object.'}},
            status=400,
        )

    full_name = payload.get('full_name', '')
    email = payload.get('email', '')
    phone_number = payload.get('phone_number', '')
    password = payload.get('password', '')
    role = payload.get('role', '')
    errors = {}

    for field, value in {
        'full_name': full_name,
        'email': email,
        'phone_number': phone_number,
        'password': password,
        'role': role,
    }.items():
        if not isinstance(value, str) or not value.strip():
            errors[field] = ['This field is required.']

    if errors:
        return JsonResponse({'error': {'code': 'validation_error', 'fields': errors}}, status=400)

    full_name = full_name.strip()
    email = email.strip().lower()
    phone_number = phone_number.strip()
    role = role.strip().lower()

    if len(full_name) > 150:
        errors['full_name'] = ['Must be 150 characters or fewer.']
    if len(email) > 150:
        errors['email'] = ['Must be 150 characters or fewer.']
    if len(phone_number) > 30:
        errors['phone_number'] = ['Must be 30 characters or fewer.']
    if role not in AccountProfile.Role.values:
        errors['role'] = ['Choose either "requester" or "donor".']

    requester_profile_data = None
    donor_profile_data = None
    if role == AccountProfile.Role.REQUESTER:
        requester_type = payload.get('requester_type', '')
        relationship = payload.get('relationship_to_patient', '')
        if not isinstance(requester_type, str) or requester_type not in RequesterProfile.RequesterType.values:
            errors['requester_type'] = ['Choose either "patient" or "representative".']
        if not isinstance(relationship, str):
            errors['relationship_to_patient'] = ['Enter a text value.']
        else:
            relationship = relationship.strip()
            if len(relationship) > 100:
                errors['relationship_to_patient'] = ['Must be 100 characters or fewer.']
            if requester_type == RequesterProfile.RequesterType.REPRESENTATIVE and not relationship:
                errors['relationship_to_patient'] = ['Enter the requester’s relationship to the patient.']
        requester_profile_data = {
            'requester_type': requester_type,
            'relationship_to_patient': relationship if isinstance(relationship, str) else '',
        }
    elif role == AccountProfile.Role.DONOR:
        blood_type_id = payload.get('blood_type_id')
        barangay_id = payload.get('barangay_id')
        availability = payload.get('availability_status', DonorProfile.Availability.AVAILABLE)
        raw_last_donation = payload.get('last_donation_date', '')
        last_donation_date = None

        try:
            blood_type_id = int(blood_type_id)
            blood_type = BloodType.objects.get(pk=blood_type_id)
        except (TypeError, ValueError, BloodType.DoesNotExist):
            errors['blood_type_id'] = ['Choose a blood type from GET /api/lookups/.']
            blood_type = None
        try:
            barangay_id = int(barangay_id)
            barangay = Barangay.objects.get(pk=barangay_id)
        except (TypeError, ValueError, Barangay.DoesNotExist):
            errors['barangay_id'] = ['Choose a barangay from GET /api/lookups/.']
            barangay = None

        if not isinstance(availability, str) or availability not in DonorProfile.Availability.values:
            errors['availability_status'] = ['Choose either "available" or "unavailable".']
        if raw_last_donation in (None, ''):
            last_donation_date = None
        elif not isinstance(raw_last_donation, str) or (last_donation_date := parse_date(raw_last_donation)) is None:
            errors['last_donation_date'] = ['Use YYYY-MM-DD, or leave this field empty.']
        elif last_donation_date > date.today():
            errors['last_donation_date'] = ['The last donation date cannot be in the future.']

        donor_profile_data = {
            'blood_type': blood_type,
            'barangay': barangay,
            'availability_status': availability,
            'last_donation_date': last_donation_date,
        }

    User = get_user_model()
    try:
        User._meta.get_field('email').clean(email, None)
    except ValidationError as exc:
        errors['email'] = exc.messages
    if email and User.objects.filter(email__iexact=email).exists():
        errors['email'] = ['An account with this email already exists.']
    if isinstance(password, str) and password:
        try:
            password_validation.validate_password(password)
        except ValidationError as exc:
            errors['password'] = exc.messages

    if errors:
        return JsonResponse({'error': {'code': 'validation_error', 'fields': errors}}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
            )
            profile = AccountProfile.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                role=role,
            )
            if requester_profile_data is not None:
                RequesterProfile.objects.create(user=user, **requester_profile_data)
            else:
                last_donation_date = donor_profile_data['last_donation_date']
                in_cooldown = (
                    last_donation_date is not None
                    and add_months(last_donation_date, 3) > date.today()
                )
                DonorProfile.objects.create(
                    user=user,
                    eligibility_status=(
                        DonorProfile.Eligibility.COOLDOWN
                        if in_cooldown else DonorProfile.Eligibility.ELIGIBLE
                    ),
                    **donor_profile_data,
                )
    except IntegrityError:
        return JsonResponse(
            {'error': {'code': 'email_exists', 'message': 'An account with this email already exists.'}},
            status=409,
        )

    response_user = {
        'user_id': user.pk,
        'full_name': profile.full_name,
        'email': user.email,
        'phone_number': profile.phone_number,
        'role': profile.role,
        'account_status': profile.account_status,
        'created_at': timezone.localtime(profile.created_at).isoformat(),
    }
    if profile.role == AccountProfile.Role.REQUESTER:
        requester = user.requester_profile
        response_user['requester_profile'] = {
            'requester_type': requester.requester_type,
            'relationship_to_patient': requester.relationship_to_patient,
        }
    else:
        donor = user.donor_profile
        response_user['donor_profile'] = {
            'blood_type': donor.blood_type.code,
            'barangay': {'id': donor.barangay_id, 'name': donor.barangay.name, 'city': donor.barangay.city},
            'availability_status': donor.availability_status,
            'eligibility_status': donor.eligibility_status,
            'last_donation_date': donor.last_donation_date.isoformat() if donor.last_donation_date else None,
        }

    return JsonResponse({
        'message': 'Registration successful.',
        'user': response_user,
    }, status=201)


def lookups(request):
    if request.method != 'GET':
        return JsonResponse(
            {'error': {'code': 'method_not_allowed', 'message': 'Use GET for lookup data.'}},
            status=405,
        )
    return JsonResponse({
        'blood_types': list(BloodType.objects.values('id', 'code')),
        'barangays': list(Barangay.objects.values('id', 'name', 'city')),
    })
