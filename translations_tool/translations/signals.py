def add_history_language(sender, **kwargs):
    from translations_tool.translations.models import LanguageHistoricalModel

    if not issubclass(sender, LanguageHistoricalModel):
        return

    history_instance = kwargs["history_instance"]

    if not history_instance.prev_record:
        return

    changed_fields = history_instance.diff_against(history_instance.prev_record).changed_fields
    changed_fields_languages = set(field.split("_")[-1] for field in changed_fields)
    if len(changed_fields_languages) == 1:
        history_instance.language = next(iter(changed_fields_languages))
