# Generated by Django 4.2.1 on 2023-06-10 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('image_url', models.URLField(blank=True, null=True)),
                ('sentiment', models.CharField(max_length=10)),
            ],
        ),
    ]
