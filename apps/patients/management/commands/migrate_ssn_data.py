from django.core.management.base import BaseCommand
from django.db import transaction
from apps.patients.models import Patient


class Command(BaseCommand):
    help = 'Migrate SSN data from legacy format to new format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process per batch'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes'
        )
        parser.add_argument(
            '--rollback',
            action='store_true',
            help='Rollback migration (new format to legacy)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        rollback = options['rollback']

        if rollback:
            self.rollback_migration(batch_size, dry_run)
        else:
            self.migrate_forward(batch_size, dry_run)

    def migrate_forward(self, batch_size, dry_run):
        self.stdout.write('Starting SSN migration (legacy to new format)...')
        
        patients = Patient.objects.filter(
            ssn_legacy__isnull=False,
            ssn_number=''
        ).exclude(ssn_legacy='')

        total = patients.count()
        self.stdout.write(f'Found {total} patients to migrate')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            return

        migrated = 0
        for i in range(0, total, batch_size):
            batch = patients[i:i + batch_size]
            
            with transaction.atomic():
                for patient in batch:
                    patient.ssn_number = patient.ssn_legacy
                    patient.ssn_verified = False
                    patient.save(update_fields=[
                        'ssn_number',
                        'ssn_verified'
                    ])
                    migrated += 1

            self.stdout.write(f'Migrated {migrated}/{total} patients')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated} patients')
        )

    def rollback_migration(self, batch_size, dry_run):
        self.stdout.write('Starting SSN rollback (new format to legacy)...')
        
        patients = Patient.objects.filter(
            ssn_number__isnull=False
        ).exclude(ssn_number='')

        total = patients.count()
        self.stdout.write(f'Found {total} patients to rollback')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            return

        rolled_back = 0
        for i in range(0, total, batch_size):
            batch = patients[i:i + batch_size]
            
            with transaction.atomic():
                for patient in batch:
                    if not patient.ssn_legacy:
                        patient.ssn_legacy = patient.ssn_number
                    patient.ssn_number = ''
                    patient.ssn_verified = False
                    patient.ssn_verification_date = None
                    patient.save(update_fields=[
                        'ssn_legacy',
                        'ssn_number',
                        'ssn_verified',
                        'ssn_verification_date'
                    ])
                    rolled_back += 1

            self.stdout.write(f'Rolled back {rolled_back}/{total} patients')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully rolled back {rolled_back}')
        )