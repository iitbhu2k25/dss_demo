# Generated by Django 5.1.5 on 2025-02-07 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Data",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("state", models.IntegerField()),
                ("district", models.IntegerField()),
                ("subdistrict", models.IntegerField()),
                ("village", models.IntegerField()),
                ("name", models.CharField(max_length=100)),
                ("sewage_gap", models.FloatField()),
                ("mean_temperature", models.FloatField()),
                ("mean_rainfall", models.FloatField()),
                ("number_of_tourists", models.IntegerField()),
                ("water_quality_index", models.FloatField()),
                ("number_of_asi_sites", models.IntegerField()),
                ("gdp_at_current_prices", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Weight",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sewage_gap", models.FloatField()),
                ("mean_temperature", models.FloatField()),
                ("mean_rainfall", models.FloatField()),
                ("number_of_tourists", models.FloatField()),
                ("water_quality_index", models.FloatField()),
                ("number_of_asi_sites", models.FloatField()),
                ("gdp_at_current_prices", models.FloatField()),
            ],
        ),
    ]
