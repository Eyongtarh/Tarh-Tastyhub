"""
One-off backfill for dishes saved before Dish.image_card existed. New
saves generate it automatically (see Dish._compress_image_field), but
that only runs on save() - existing rows need this run once to get a
grid-card-sized image instead of falling back to the full-size one.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q

from dishes.models import Dish


class Command(BaseCommand):
    help = "Generate the missing image_card variant for existing dishes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Regenerate image_card for every dish with an image, "
                "including ones that already have one (e.g. after "
                "changing card_max_size/card_quality)."
            ),
        )

    def handle(self, *args, **options):
        dishes = Dish.objects.exclude(image="")
        if not options["force"]:
            dishes = dishes.filter(Q(image_card="") | Q(image_card__isnull=True))
        total = dishes.count()
        updated = 0
        for dish in dishes:
            try:
                dish._compress_image_field("image")
                updated += 1
                self.stdout.write(f"Generated image_card for: {dish.name}")
            except Exception as exc:
                self.stderr.write(f"Skipped {dish.name}: {exc}")

        self.stdout.write(self.style.SUCCESS(
            f"{updated}/{total} dish(es) updated with an image_card."
        ))
