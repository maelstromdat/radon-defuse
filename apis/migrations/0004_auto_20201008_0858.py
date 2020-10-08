# Generated by Django 3.1.2 on 2020-10-08 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_auto_20201006_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repositories',
            name='id',
            field=models.CharField(max_length=40, primary_key=True, serialize=False, unique=True),
        ),
        migrations.CreateModel(
            name='FixingFile',
            fields=[
                ('auto_id', models.AutoField(primary_key=True, serialize=False)),
                ('is_false_positive', models.BooleanField(blank=True, default=False)),
                ('filepath', models.CharField(editable=False, max_length=300)),
                ('bug_inducing_commit', models.CharField(editable=False, max_length=50)),
                ('fixing_commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.fixingcommit')),
            ],
        ),
    ]
