from django.db import models

# Create your models here.
class FileUpload(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='uploads/')