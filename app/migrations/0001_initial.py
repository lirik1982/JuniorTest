# Generated by Django 4.2.4 on 2023-08-15 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.CharField(max_length=50)),
                ('item', models.CharField(max_length=50)),
                ('total', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('date', models.DateTimeField()),
            ],
        ),
    ]
