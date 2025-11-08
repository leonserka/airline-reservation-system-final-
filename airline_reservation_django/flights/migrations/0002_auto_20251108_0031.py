from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='departure_country',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='flight',
            name='arrival_country',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
