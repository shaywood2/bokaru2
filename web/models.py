from django.db import models


class User(models.Model):
    displayName = models.CharField(max_length=200, null=False, unique=True)
    email = models.EmailField(max_length=200, null=False, unique=True)
    name = models.CharField(max_length=200)
    birthDate = models.DateField()
    STATUSES = (
        ('created', 'Created'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('deleted', 'Deleted')
    )
    status = models.CharField(max_length=20, choices=STATUSES)
    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.displayName + ' (' + self.email + ')'
