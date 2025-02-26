from django.db import models
from django.contrib.gis.db import models as gis_models

# Create your models here.
class raster_visual(gis_models.Model):
    name=models.TextField(max_length=50) #groundwater
    year = models.IntegerField(help_text="Year of the raster data")
    resolution = models.FloatField(blank=True, null=True, help_text="Spatial resolution in map units")
    phase=models.CharField(max_length=10,default=None)
    rast=gis_models.RasterField(srid=4326,spatial_index=True,null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['year']),
        ]
        ordering = ['year']
    def __str__(self):
        return f"{self.name}-{self.dates}"

    