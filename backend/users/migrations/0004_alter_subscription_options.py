# Generated by Django 3.2.3 on 2024-07-20 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_subscription_subscribe_to_yourself'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
