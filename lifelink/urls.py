"""URL configuration and small, in-memory map demo for LifeLink."""
from math import asin, cos, radians, sin, sqrt
import os
from pathlib import Path
from datetime import date, timedelta

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


BLOOD_TYPES = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
URGENCY_LEVELS = {
    'immediate': 'Immediate',
    'six_hours': 'Within 6 hours',
    'today': 'Today',
    'scheduled': 'Scheduled / planned',
}
REQUESTER_ROLES = {
    'patient': 'I am the patient',
    'representative': 'I am requesting on behalf of a patient',
}

# Demo data only. Coordinates are approximate; replace with verified hospital
# and barangay coordinates before using this for real requests.
HOSPITALS = [
    {'id': 'qcgh', 'name': 'Quezon City General Hospital', 'address': 'Seminary Road, Barangay Bahay Toro, Project 8, Quezon City', 'coords': [14.66092, 121.01869]},
    {'id': 'ndh', 'name': 'Novaliches District Hospital', 'address': '683 Quirino Highway, Barangay San Bartolome, Novaliches, Quezon City', 'coords': [14.70054, 121.03438]},
    {'id': 'rmbgh', 'name': 'Rosario Maclang Bautista General Hospital', 'address': 'IBP Road, Batasan Hills, Quezon City', 'coords': [14.6861, 121.0891]},
    {'id': 'qmmc', 'name': 'Quirino Memorial Medical Center', 'address': 'Project 4, Quezon City', 'coords': [14.62221, 121.0722]},
    {'id': 'eamc', 'name': 'East Avenue Medical Center', 'address': 'East Avenue, Diliman, Quezon City', 'coords': [14.64191, 121.04792]},
    {'id': 'nkti', 'name': 'National Kidney and Transplant Institute', 'address': 'East Avenue, Diliman, Quezon City', 'coords': [14.64725, 121.04725]},
    {'id': 'phc', 'name': 'Philippine Heart Center', 'address': 'East Avenue, Diliman, Quezon City', 'coords': [14.64392, 121.04842]},
    {'id': 'lung-center', 'name': 'Lung Center of the Philippines', 'address': 'Quezon Avenue, Barangay Central, Diliman, Quezon City', 'coords': [14.64747, 121.04574]},
    {'id': 'pcmc', 'name': 'Philippine Children’s Medical Center', 'address': 'Quezon Avenue, Quezon City', 'coords': [14.64759, 121.04144]},
    {'id': 'vmmc', 'name': 'Veterans Memorial Medical Center', 'address': 'North Avenue, Diliman, Quezon City', 'coords': [14.65651, 121.04005]},
]

# Small ZIP-code demo lookup, not a complete postal-code/geocoding service.
ZIP_LOCATIONS = {
    '1109': {'area': 'Project 4', 'coords': [14.6308, 121.0561]},
    '1121': {'area': 'Commonwealth', 'coords': [14.7002, 121.0847]},
    '1126': {'area': 'Batasan Hills', 'coords': [14.6775, 121.0965]},
}

# Fictional donor records for the matching demo only; replace with database data.
SAMPLE_DONORS = [
    {'id': 'donor-a', 'name': 'Donor A (sample)', 'barangay': 'Project 4', 'blood_type': 'O+', 'available': True, 'last_donation': date.today() - timedelta(days=165), 'coords': [14.6308, 121.0561]},
    {'id': 'donor-b', 'name': 'Donor B (sample)', 'barangay': 'Batasan Hills', 'blood_type': 'A+', 'available': True, 'last_donation': date.today() - timedelta(days=135), 'coords': [14.6775, 121.0965]},
    {'id': 'donor-c', 'name': 'Donor C (sample)', 'barangay': 'Commonwealth', 'blood_type': 'O-', 'available': True, 'last_donation': date.today() - timedelta(days=210), 'coords': [14.7002, 121.0847]},
    {'id': 'donor-d', 'name': 'Donor D (sample)', 'barangay': 'Cubao', 'blood_type': 'B+', 'available': True, 'last_donation': date.today() - timedelta(days=190), 'coords': [14.6198, 121.0567]},
    {'id': 'donor-e', 'name': 'Donor E (sample)', 'barangay': 'Kamuning', 'blood_type': 'A-', 'available': True, 'last_donation': date.today() - timedelta(days=55), 'coords': [14.6351, 121.0383]},
    {'id': 'donor-f', 'name': 'Donor F (sample)', 'barangay': 'Loyola Heights', 'blood_type': 'A+', 'available': False, 'last_donation': date.today() - timedelta(days=220), 'coords': [14.6401, 121.0752]},
]

# Simplified red-cell compatibility for demonstration; hospitals must verify.
COMPATIBLE_DONOR_TYPES = {
    'O-': ['O-'], 'O+': ['O-', 'O+'], 'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'], 'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'], 'AB+': BLOOD_TYPES,
}


def distance_km(point_a, point_b):
    """Return straight-line distance between [latitude, longitude] pairs."""
    lat1, lon1 = map(radians, point_a)
    lat2, lon2 = map(radians, point_b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    haversine = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(haversine))


def map_test(request):
    # Read the ignored local .env file so the CARTO key remains out of source.
    env_path = Path(__file__).resolve().parent.parent / '.env'
    file_key = ''
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            if line.strip().startswith('CARTO_API_KEY='):
                file_key = line.split('=', 1)[1].strip().strip('"\'')
                break

    data = request.POST if request.method == 'POST' else request.GET
    action = data.get('action', '')
    blood_type = data.get('blood_type', 'A+')
    if blood_type not in BLOOD_TYPES:
        blood_type = 'A+'
    urgency = data.get('urgency', 'today')
    if urgency not in URGENCY_LEVELS:
        urgency = 'today'
    requester_role = data.get('requester_role', 'representative')
    if requester_role not in REQUESTER_ROLES:
        requester_role = 'representative'
    zip_code = data.get('zip_code', '').strip()
    location = ZIP_LOCATIONS.get(zip_code)
    details = data.get('details', '').strip()[:300]

    suggestions = []
    if location:
        # ZIP code identifies the request area; the requester chooses the
        # hospital where the patient is receiving care. It is not a ranking.
        suggestions = HOSPITALS[:]

    zip_error = ''
    if action == 'find_hospitals' and not location:
        zip_error = 'For this demo, use 1109, 1121, or 1126.'

    requested_hospital_id = data.get('hospital', '')
    selected_hospital = next(
        (hospital for hospital in suggestions if hospital['id'] == requested_hospital_id),
        None,
    )
    if action == 'find_hospitals' and suggestions and selected_hospital is None:
        selected_hospital = suggestions[0]

    request_submitted = action in ('submit_request', 'confirm_donors') and location is not None and selected_hospital is not None
    request_error = ''
    if action == 'submit_request' and not request_submitted:
        request_error = 'Enter a supported ZIP code, show the hospital list, and select where the patient is being treated.'

    donor_matches = []
    if request_submitted:
        eligible_types = COMPATIBLE_DONOR_TYPES[blood_type]
        for donor in SAMPLE_DONORS:
            if not donor['available'] or donor['blood_type'] not in eligible_types:
                continue
            if donor['last_donation'] + timedelta(days=90) > date.today():
                continue
            donor_distance = round(distance_km(selected_hospital['coords'], donor['coords']), 1)
            if donor_distance > 25:
                continue
            donor_matches.append({
                'id': donor['id'],
                'name': donor['name'],
                'barangay': donor['barangay'],
                'blood_type': donor['blood_type'],
                'distance_km': donor_distance,
                'last_donation': donor['last_donation'].strftime('%b %d, %Y'),
                'available': donor['available'],
                'coords': donor['coords'],
            })
        donor_matches.sort(key=lambda donor: donor['distance_km'])

    selected_donor_ids = set(data.getlist('selected_donors')) if request.method == 'POST' else set()
    eligible_donor_ids = {donor['id'] for donor in donor_matches}
    selected_donor_ids &= eligible_donor_ids
    donors_confirmed = action == 'confirm_donors' and bool(selected_donor_ids)
    donor_selection_error = action == 'confirm_donors' and not selected_donor_ids

    return render(request, 'map_test.html', {
        'carto_api_key': file_key or os.getenv('CARTO_API_KEY', ''),
        'blood_types': BLOOD_TYPES,
        'selected_blood_type': blood_type,
        'urgency_levels': URGENCY_LEVELS,
        'selected_urgency': urgency,
        'urgency_label': URGENCY_LEVELS[urgency],
        'requester_roles': REQUESTER_ROLES,
        'selected_requester_role': requester_role,
        'zip_code': zip_code,
        'lookup_area': location['area'] if location else '',
        'hospital_suggestions': suggestions,
        'selected_hospital_id': selected_hospital['id'] if selected_hospital else '',
        'selected_hospital': selected_hospital,
        'selected_hospital_json': selected_hospital,
        'donor_matches_json': donor_matches,
        'zip_error': zip_error,
        'request_error': request_error,
        'request_details': details,
        'request_submitted': request_submitted,
        'lookup_done': action == 'find_hospitals' and location is not None,
        'donor_matches': donor_matches,
        'matching_done': request_submitted,
        'selected_donor_ids': selected_donor_ids,
        'donors_confirmed': donors_confirmed,
        'donor_selection_error': donor_selection_error,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('', map_test, name='home'),
    path('map-test/', map_test, name='map_test'),
]
