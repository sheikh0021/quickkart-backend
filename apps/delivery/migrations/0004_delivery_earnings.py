# Generated manually for DeliveryEarnings model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_rename_location_longtitude_location_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryEarnings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='earnings', to='delivery.deliveryassignment')),
                ('delivery_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earnings', to='users.user')),
            ],
            options={
                'ordering': ['-earned_at'],
            },
        ),
    ]