from django.db import migrations


BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
QUEZON_CITY_BARANGAYS = [
    'Batasan Hills',
    'Commonwealth',
    'Bahay Toro',
    'San Bartolome',
]


def seed_lookups(apps, schema_editor):
    BloodType = apps.get_model('accounts', 'BloodType')
    Barangay = apps.get_model('accounts', 'Barangay')
    BloodType.objects.using(schema_editor.connection.alias).bulk_create(
        [BloodType(code=code) for code in BLOOD_TYPES],
        ignore_conflicts=True,
    )
    Barangay.objects.using(schema_editor.connection.alias).bulk_create(
        [Barangay(name=name, city='Quezon City') for name in QUEZON_CITY_BARANGAYS],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_bloodtype_requesterprofile_barangay_donorprofile'),
    ]

    operations = [
        migrations.RunPython(seed_lookups, migrations.RunPython.noop),
    ]
