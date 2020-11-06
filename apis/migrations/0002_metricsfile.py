# Generated by Django 3.1.3 on 2020-11-06 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricsFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.BinaryField()),
                ('language', models.CharField(max_length=50)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.repositories')),
            ],
        ),
    ]
