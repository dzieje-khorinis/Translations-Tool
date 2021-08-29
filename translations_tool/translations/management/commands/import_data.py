import argparse
import json
import re

from django.core.management.base import BaseCommand

from translations_tool.translations.models import Translation, TranslationGroup

PATTERN = re.compile(r"[a-zA-Z]")


class Command(BaseCommand):
    help = "Imports translation from json data"

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=argparse.FileType("r"),
            help="Path to the data file",
        )

    def handle(self, *args, **options):
        file = options["path"]
        data = json.loads(file.read())
        print(len(data))
        Translation.objects.all().delete()
        TranslationGroup.objects.all().delete()

        count = len(data)
        for i, row in enumerate(data, start=1):
            key = (row["key"] or "").strip()
            key_from_value = False
            value = row["value_pl"].strip()

            value_as_key = value.upper()
            nonempty_value = PATTERN.search(value_as_key)

            if not key and nonempty_value:
                key = f"{value_as_key}_VALUE"
                key_from_value = True

            if not PATTERN.search(key) or not nonempty_value:
                continue

            print(f"{i}/{count}")
            prev_group = None
            for group_name in row["group"].split("."):
                assert group_name

                prev_group, created = TranslationGroup.objects.get_or_create(
                    name_en=group_name,
                    name_pl=group_name,
                    name_de=group_name,
                    name_ru=group_name,
                    parent=prev_group,
                )

            creation_kwargs = {
                "key": key,
                "value_pl": value,
                "parent": prev_group,
            }
            path = row["metadata"]["path"]
            line = row["metadata"]["line"]
            if path:
                creation_kwargs["file"] = path
            if line:
                creation_kwargs["line"] = line

            try:
                translation = Translation.objects.get(key=key)
                if not (key_from_value or translation.value_pl == value):
                    print(key, row)
                    raise
                continue
            except Translation.DoesNotExist:
                pass

            Translation.objects.get_or_create(**creation_kwargs)
