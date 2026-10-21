# LifeLink Registration API

This contract covers registration only. An account selects one role (`requester` or `donor`) and the API creates the matching profile. Login, blood requests, donor matching, and notifications are outside this registration scope.

Base URL during local development: `http://127.0.0.1:8000/api/`

## Get registration choices

`GET /api/lookups/`

Returns the blood types and barangays used by the donor registration form. Use the returned IDs in the donor registration request.

```json
{
  "blood_types": [
    {"id": 1, "code": "A+"}
  ],
  "barangays": [
    {"id": 1, "name": "Batasan Hills", "city": "Quezon City"}
  ]
}
```

The development seed contains all eight blood types and the 142 Quezon City barangay names listed by the Philippine Statistics Authority's Philippine Standard Geographic Code (PSGC). This is a name catalog for the barangay dropdown; it does not yet include map coordinates.

## Register an account

`POST /api/register/` with `Content-Type: application/json`.

Shared fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `full_name` | Yes | Account holder's name |
| `email` | Yes | Login email; must be unique |
| `phone_number` | Yes | Contact number |
| `password` | Yes | Validated and stored as a Django password hash |
| `role` | Yes | `requester` or `donor` |

Requester fields (`role: "requester"`):

| Field | Required | Meaning |
| --- | --- | --- |
| `requester_type` | Yes | `patient` or `representative` |
| `relationship_to_patient` | For representatives | Relationship to the patient; up to 100 characters |

Example requester request:

```json
{
  "full_name": "Sample Requester",
  "email": "requester@example.com",
  "phone_number": "+639123456789",
  "password": "ChooseAStrongPassword123!",
  "role": "requester",
  "requester_type": "representative",
  "relationship_to_patient": "Sibling"
}
```

Donor fields (`role: "donor"`):

| Field | Required | Meaning |
| --- | --- | --- |
| `blood_type_id` | Yes | `id` returned by `GET /api/lookups/` |
| `barangay_id` | Yes | `id` returned by `GET /api/lookups/` |
| `availability_status` | No | `available` or `unavailable`; defaults to `available` |
| `last_donation_date` | No | `YYYY-MM-DD` or `null` |

Example donor request:

```json
{
  "full_name": "Sample Donor",
  "email": "donor@example.com",
  "phone_number": "+639123456789",
  "password": "ChooseAStrongPassword123!",
  "role": "donor",
  "blood_type_id": 1,
  "barangay_id": 1,
  "availability_status": "available",
  "last_donation_date": "2026-03-12"
}
```

Successful registration returns HTTP `201`, the new account ID, shared account fields, and the created role-specific profile. The password is never returned.

Donor `eligibility_status` is derived from the three-calendar-month interval and the submitted last donation date. It only represents the donation interval; it is not a medical clearance.

## Error responses

- `400 validation_error`: invalid or missing values, returned with field-specific messages.
- `409 email_exists`: email conflict detected during account creation.
- `415 unsupported_media_type`: request did not use JSON.

The database models follow the current ERD. Date of birth is not included because it is not currently in the ERD, so registration does not enforce the age rule discussed in the meeting.
