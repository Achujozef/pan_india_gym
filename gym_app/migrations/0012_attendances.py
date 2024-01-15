# Generated by Django 4.2.1 on 2023-06-07 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0011_remove_assigntrainer_added_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent')], max_length=10)),
                ('attendance_date', models.DateField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.extendedusermodel')),
            ],
        ),
    ]