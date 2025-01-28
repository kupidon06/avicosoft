from django.db import connection, IntegrityError
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.core.management.base import BaseCommand


def get_tenant_model():
    try:
        return apps.get_model(settings.TENANT_MODEL)
    except AttributeError:
        raise ImproperlyConfigured("TENANT_MODEL must be defined in settings.")
    except LookupError:
        raise ImproperlyConfigured("TENANT_MODEL points to a non-existent model.")


def get_domain_model():
    try:
        return apps.get_model(settings.DOMAIN_MODEL)
    except AttributeError:
        raise ImproperlyConfigured("DOMAIN_MODEL must be defined in settings.")
    except LookupError:
        raise ImproperlyConfigured("DOMAIN_MODEL points to a non-existent model.")


def migrate_tenant_schemas():
    Tenant = get_tenant_model()
    tenants = Tenant.objects.all()

    for tenant in tenants:
        with connection.cursor() as cursor:
            # Set search_path to the tenant schema
            cursor.execute(f"SET search_path TO {tenant.schema_name};")
            print(f"Migrating schema: {tenant.schema_name}")
            
            # Execute migrations for this specific schema
            try:
                call_command('migrate', database=tenant.schema_name, interactive=False)
            except Exception as e:
                print(f"Error migrating schema {tenant.schema_name}: {str(e)}")


def create_tenant(name, schema_name, domain):
    """
    Create a new tenant and its associated domain if they do not already exist.
    """
    Tenant = get_tenant_model()
    Domain = get_domain_model()

    # Check if the schema or domain already exists
    if Tenant.objects.filter(schema_name=schema_name).exists():
        raise ValidationError(f"A tenant with the schema '{schema_name}' already exists.")
    if Domain.objects.filter(domain=domain).exists():
        raise ValidationError(f"A domain with the name '{domain}' already exists.")

    try:
        # Create the schema
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

        # Create the tenant
        tenant = Tenant.objects.create(name=name, schema_name=schema_name)

        # Create the domain
        Domain.objects.create(domain=domain, tenant=tenant)

        return tenant

    except IntegrityError as e:
        raise ValidationError(f"Integrity error: {str(e)}")
    except Exception as e:
        # Drop the schema if something goes wrong
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
        raise ValidationError(f"Critical error while creating the tenant: {str(e)}")


def switch_tenant(schema_name):
    """
    Switch the database schema to the specified tenant schema.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO %s;", [schema_name])
    except Exception as e:
        raise ValidationError(f"Unable to switch schema: {str(e)}")


class Command(BaseCommand):
    help = "Performs migrations for each existing tenant schema, creating the schema if necessary."

    def handle(self, *args, **options):
        Tenant = get_tenant_model()
        tenants = Tenant.objects.all()

        for tenant in tenants:
            self.stdout.write(f"Processing tenant: {tenant.schema_name}")

            # Check if the schema exists
            if not self.schema_exists(tenant.schema_name):
                self.stdout.write(f"Schema {tenant.schema_name} not found. Creating...")
                self.create_schema(tenant.schema_name)
            else:
                self.stdout.write(f"Schema {tenant.schema_name} already exists.")

            # Set the search_path to the current tenant schema
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {tenant.schema_name};")
                    self.stdout.write(f"Migrating schema: {tenant.schema_name}")
                    call_command('migrate', interactive=False)
            except OperationalError as e:
                self.stderr.write(f"Error during migration for {tenant.schema_name}: {str(e)}")

        self.stdout.write(self.style.SUCCESS("Migrations completed for all tenants."))

    def schema_exists(self, schema_name):
        """
        Checks if a PostgreSQL schema exists.
        """
        query = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [schema_name])
            return cursor.fetchone() is not None

    def create_schema(self, schema_name):
        """
        Creates a new PostgreSQL schema.
        """
        query = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        with connection.cursor() as cursor:
            cursor.execute(query)
        self.stdout.write(f"Schema {schema_name} created successfully.")
