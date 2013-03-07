from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from smrt.services import SmrtService


class Area(models.Model):
    name = models.CharField(max_length=64)
    feed_url = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now_add=True, auto_now=True)


class Article(models.Model):
    area = models.ForeignKey(Area)
    category = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    published = models.DateField()
    updated = models.DateTimeField()
    link = models.CharField(max_length=200)
    summary = models.TextField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    wordcount = models.PositiveSmallIntegerField()


@receiver(post_save, sender=Article)
def on_play_save(sender, instance=False, created=False, **kwargs):
    SmrtService().index_article(instance)
    SmrtService().commit()
