# Generated by Django 3.1.13 on 2024-02-09 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cves', '0016_auto_20230118_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalproduct',
            name='name',
            field=models.TextField(db_index=True, default='-', max_length=250),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.TextField(db_index=True, default='-', max_length=250),
        ),
    ]
