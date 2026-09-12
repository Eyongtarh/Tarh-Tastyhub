"""
Fixes the django.contrib.sites Site record, which was set to a domain
this app doesn't actually serve (tarh-tastyhub.com). That value feeds
every {{ current_site.domain }} email link (order confirmations,
allauth's own signup/email-confirmation templates) and the sitemap -
all of them were pointing somewhere that isn't this site.
"""
from django.conf import settings
from django.db import migrations


def fix_site_domain(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    real_domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "localhost"
    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": real_domain, "name": "Tarh Tastyhub"},
    )


def noop_reverse(apps, schema_editor):
    # Not worth restoring the broken domain on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(fix_site_domain, noop_reverse),
    ]
