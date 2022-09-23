import argparse
import json
import re

from django.core.management.base import BaseCommand

from translations_tool.translations.models import (
    Directory,
    Translation,
    TranslationGroup,
)

PATTERN = re.compile(r"[a-zA-Z]")


class Command(BaseCommand):
    help = "Imports translation from json data"

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=argparse.FileType("r"),
            help="Path to the data file",
        )
        parser.add_argument(
            "--lang",
            "-l",
            type=str,
            required=True,
        )

    def handle(self, *args, **options):
        file = options["path"]
        lang = options["lang"]
        data = json.loads(file.read())
        print(len(data))
        Translation.objects.all().delete()
        TranslationGroup.objects.all().delete()
        Directory.objects.all().delete()

        count = len(data)
        for i, row in enumerate(data, start=1):
            key = (row["key"] or "").strip()
            key_from_value = False
            value = row[f"value_{lang}"].strip()

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

            filepath = row["metadata"]["path"]
            if not filepath:
                continue

            creation_kwargs = {
                "key": key,
                f"value_{lang}": value,
                "parent": prev_group,
                "file": filepath,
                "line": row["metadata"]["line"],
            }

            try:
                translation = Translation.objects.get(key=key)
                if not (key_from_value or getattr(translation, f"value_{lang}") == value):
                    print("ALERT!!!", key, row)
                    raise
                continue
            except Translation.DoesNotExist:
                pass

            translation, _ = Translation.objects.get_or_create(**creation_kwargs)

            parent = None
            path = ""
            *parts, last_part = filepath.strip("/").split("/")
            for part in parts:
                path += f"/{part}"
                parent, _ = Directory.objects.get_or_create(name=part, path=path, parent=parent)

            path += f"/{last_part}"
            parent, _ = Directory.objects.get_or_create(name=last_part, path=path, parent=parent, leaf=True)
