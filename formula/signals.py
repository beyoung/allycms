from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from os import environ

from formula.exceptions import ReadonlyException


def prevent_modifications(sender, instance, **kwargs):
    # Check if readonly mode is explicitly enabled via environment variable
    readonly_mode = environ.get("READONLY_MODE", "0") == "1"
    
    if readonly_mode and sender._meta.db_table != "studio_options":
        raise ReadonlyException(
            "Database is operating in readonly mode. Not possible to save any data."
        )


@receiver(pre_save)
def block_save(sender, instance, **kwargs):
    prevent_modifications(sender, instance, **kwargs)


@receiver(pre_delete)
def block_delete(sender, instance, **kwargs):
    prevent_modifications(sender, instance, **kwargs)
