from django.db import models


class Weight(models.Model):
    sewage_gap = models.FloatField()
    mean_temperature = models.FloatField()
    mean_rainfall = models.FloatField()
    number_of_tourists = models.FloatField()
    water_quality_index = models.FloatField()
    number_of_asi_sites = models.FloatField()
    gdp_at_current_prices = models.FloatField()

    class Meta:
        app_label = 'stp'

class Data(models.Model):
    id=models.AutoField(primary_key=True)
    state = models.IntegerField()
    district = models.IntegerField()
    subdistrict = models.IntegerField()
    village = models.IntegerField()
    name = models.CharField(max_length=100)
    sewage_gap = models.FloatField()
    mean_temperature = models.FloatField()
    mean_rainfall = models.FloatField()
    number_of_tourists = models.IntegerField()
    water_quality_index = models.FloatField()
    number_of_asi_sites = models.IntegerField()
    gdp_at_current_prices = models.IntegerField()

    class Meta:
        app_label = 'stp'   

    def __str__(self):
        return f"{self.state}-{self.district}-{self.sub_district}-{self.village}: {self.name}"
