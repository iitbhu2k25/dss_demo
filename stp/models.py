from django.db import models
from django.contrib.gis.db import models as modelss

class State(models.Model):
    state_id=models.IntegerField()
    state_name=models.CharField(max_length=30)

    class Meta:
        app_label = 'stp'
    def __str__(self):
        return self.state_name

class District(models.Model):
    district_id=models.IntegerField()
    district_name=models.CharField(max_length=30)
    state_id=models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        app_label = 'stp'

class Sub_district(models.Model):
    id = models.AutoField(primary_key=True)
    subdistrict_id=models.IntegerField()
    subdistrict_name=models.CharField(max_length=100)
    district_id=models.ForeignKey(District, on_delete=models.CASCADE)

    class Meta:
        app_label = 'stp'

class Villages(models.Model):
    village_id=models.IntegerField()
    village_name=models.CharField(max_length=100)
    subdistrict_id=models.ForeignKey(Sub_district, on_delete=models.CASCADE)
    sewage_gap=models.DecimalField(max_digits=20, decimal_places=10)
    mean_temperature=models.DecimalField(max_digits=20, decimal_places=10)
    mean_rainfall=models.DecimalField(max_digits=20, decimal_places=10)
    number_of_tourists=models.IntegerField()
    water_quality_index=models.DecimalField(max_digits=20, decimal_places=10)
    number_of_asi_sites=models.IntegerField()
    gdp_at_current_prices=models.DecimalField(max_digits=20, decimal_places=10)
    
    class Meta:
        app_label = 'stp'

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

# now we here i make the spatial table
class Stp_subdis(modelss.Model):
    state_code=modelss.IntegerField()
    state_name=modelss.CharField(max_length=255)
    dist_code=modelss.IntegerField()
    dist_name=modelss.CharField(max_length=255)
    subdis_nam=modelss.CharField(max_length=255)
    subdis_cod=modelss.IntegerField()
    geometry = modelss.GeometryField()
    def __str__(self):
        return f"{self.state_name},{self.state_code}"

  
    