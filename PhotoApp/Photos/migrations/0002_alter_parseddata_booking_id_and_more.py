# Generated by Django 4.2.4 on 2023-08-24 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Photos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parseddata',
            name='booking_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='parseddata',
            name='vehicle_model_no',
            field=models.CharField(max_length=255),
        ),
    ]
