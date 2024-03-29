# Generated by Django 5.0 on 2023-12-20 07:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finsys_App', '0002_fin_distributors_details_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fin_Staff_Details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.CharField(blank=True, max_length=255, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='image/staff')),
                ('Company_approval_status', models.CharField(blank=True, max_length=255, null=True)),
                ('Login_Id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_login_details')),
                ('company_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_company_details')),
            ],
        ),
    ]
