from django.db import migrations


# Quezon City names from the Philippine Statistics Authority PSGC listing.
# The first four were seeded in migration 0003; conflicts are ignored so this
# migration can safely add the full catalog on both existing and fresh DBs.
QUEZON_CITY_BARANGAYS = [
    'Alicia', 'Amihan', 'Apolonio Samson', 'Aurora', 'Baesa', 'Bagbag',
    'Bagumbuhay', 'Bagong Lipunan Ng Crame', 'Bagong Pag-asa',
    'Bagong Silangan', 'Bagumbayan', 'Bahay Toro', 'Balingasa', 'Bayanihan',
    'Blue Ridge A', 'Blue Ridge B', 'Botocan', 'Bungad', 'Camp Aguinaldo',
    'Central', 'Claro', 'Commonwealth', 'New Era', 'Kristong Hari', 'Culiat',
    'Damar', 'Damayan', 'Damayang Lagi', 'Del Monte', 'Dioquino Zobel',
    'Doña Imelda', 'Doña Josefa', 'Don Manuel', 'Duyan-duyan', 'E. Rodriguez',
    'East Kamias', 'Escopa I', 'Escopa II', 'Escopa III', 'Escopa IV',
    'Fairview', 'N.S. Amoranto', 'Gulod', 'Horseshoe', 'Immaculate Concepcion',
    'Kaligayahan', 'Kalusugan', 'Kamuning', 'Katipunan', 'Kaunlaran',
    'Krus Na Ligas', 'Laging Handa', 'Libis', 'Lourdes', 'Loyola Heights',
    'Maharlika', 'Malaya', 'Manresa', 'Mangga', 'Mariana', 'Mariblo', 'Marilag',
    'Masagana', 'Masambong', 'Santo Domingo', 'Matandang Balara', 'Milagrosa',
    'Nagkaisang Nayon', 'Nayong Kanluran', 'Novaliches Proper', 'Obrero',
    'Old Capitol Site', 'Paang Bundok', 'Pag-ibig Sa Nayon', 'Paligsahan',
    'Paltok', 'Pansol', 'Paraiso', 'Pasong Putik Proper', 'Pasong Tamo',
    'Phil-Am', 'Pinyahan', 'Pinagkaisahan', 'Project 6', 'Quirino 2-A',
    'Quirino 2-B', 'Quirino 2-C', 'Quirino 3-A', 'Ramon Magsaysay', 'Roxas',
    'Sacred Heart', 'Saint Ignatius', 'Saint Peter', 'Salvacion', 'San Agustin',
    'San Antonio', 'San Bartolome', 'San Isidro', 'San Isidro Labrador',
    'San Jose', 'San Martin De Porres', 'San Roque', 'San Vicente', 'Santa Cruz',
    'Santa Lucia', 'Santa Monica', 'Santa Teresita', 'Santo Cristo', 'Santo Niño',
    'Santol', 'Sauyo', 'Sienna', 'Sikatuna Village', 'Silangan', 'Socorro',
    'South Triangle', 'Tagumpay', 'Talayan', 'Talipapa', 'Tandang Sora',
    'Tatalon', 'Teachers Village East', 'Teachers Village West', 'U.P. Campus',
    'U.P. Village', 'Ugong Norte', 'Unang Sigaw', 'Valencia', 'Vasra',
    'Veterans Village', 'Villa Maria Clara', 'West Kamias', 'West Triangle',
    'White Plains', 'Balong Bato', 'Capri', 'Sangandaan', 'Payatas',
    'Batasan Hills', 'Holy Spirit', 'Greater Lagro', 'North Fairview',
]


def seed_barangays(apps, schema_editor):
    Barangay = apps.get_model('accounts', 'Barangay')
    Barangay.objects.using(schema_editor.connection.alias).bulk_create(
        [Barangay(name=name, city='Quezon City') for name in QUEZON_CITY_BARANGAYS],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_seed_registration_lookups'),
    ]

    operations = [
        migrations.RunPython(seed_barangays, migrations.RunPython.noop),
    ]
