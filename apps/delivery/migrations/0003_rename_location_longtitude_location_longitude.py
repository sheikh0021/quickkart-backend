# Generated manually to fix longitude typo

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationupdate',
            old_name='longtitude',
            new_name='longitude',
        ),
    ]