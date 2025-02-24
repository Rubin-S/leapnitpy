# Generated by Django 5.1.3 on 2024-12-03 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='chapter',
        ),
        migrations.AddField(
            model_name='question',
            name='chapter',
            field=models.ManyToManyField(related_name='questions', to='website.chapter'),
        ),
    ]
