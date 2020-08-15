from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    listing_name = models.TextField(max_length=30)
    listing_price = models.DecimalField(decimal_places=2, max_digits=6)
    listing_detail = models.TextField(max_length=40)
    image = models.ImageField()
    user  = models.ForeignKey(User, on_delete=models.CASCADE)

class Bids(models.Model):
    highestBid = models.DecimalField(decimal_places=2, max_digits=6)
    auctionListing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
class AuctionListingComments(models.Model):
    comment = models.TextField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    