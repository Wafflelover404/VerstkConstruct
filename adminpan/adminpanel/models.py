from django.db import models

class Component(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    html_content = models.TextField()
    css_content = models.TextField()

    def __str__(self):
        return self.name
