# Generated by Django 5.0 on 2024-01-02 14:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finsys_App', '0007_fin_staff_details_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ANotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Discription', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(default='New', max_length=100, null=True)),
                ('Login_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_login_details')),
            ],
        ),
        migrations.CreateModel(
            name='Payment_Terms_updation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='New', max_length=100, null=True)),
                ('Login_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_login_details')),
                ('Payment_Term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_payment_terms')),
            ],
        ),
    ]
