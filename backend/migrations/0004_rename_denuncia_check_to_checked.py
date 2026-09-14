"""Rename ``Denuncia.check`` to ``Denuncia.checked``.

The field descriptor for a model field named ``check`` overrides
``Model.check()``, which Django reports as ``models.E020`` and which stops the
system checks for the model from ever running.  The column is left alone via
``db_column``, so this migration is a no-op at the database level -- only the
Python attribute moves.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0003_fix_typos"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameField(
                    model_name="denuncia",
                    old_name="check",
                    new_name="checked",
                ),
                migrations.AlterField(
                    model_name="denuncia",
                    name="checked",
                    field=models.BooleanField(
                        db_column="check",
                        default=False,
                        null=True,
                        verbose_name="check",
                    ),
                ),
            ],
        ),
    ]
