from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.category_name}'

class Bid(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return f'{self.value} - {self.author}'

class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_listings')
    date_posted = models.DateField(default=timezone.now)
    picture_url = models.CharField(max_length=200, blank=True)
    activity = models.BooleanField(default=True)

    starting_bid = models.IntegerField()
    bids = models.ManyToManyField(Bid, blank=True)
    winner = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    watchers = models.ManyToManyField(User, related_name='watched_listings', blank=True)
    
    @property
    def current_price(self):
        current_price = int(self.starting_bid)
        for bid in self.bids.all():
            if bid.value > current_price:
                current_price = bid.value
        return current_price

    def __str__(self):
        return f'{self.title}'

class Comment(models.Model):
    content = models.CharField(max_length=300)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.author} commented {self.listing.title} on {self.date_posted}'
