from django.db import models


class Place(models.Model):
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=500)
    shortName = models.CharField(max_length=150)
    lat = models.FloatField()
    lng = models.FloatField()

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
