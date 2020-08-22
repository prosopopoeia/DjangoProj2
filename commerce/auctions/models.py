from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    listing_name = models.TextField(max_length=30)
    listing_price = models.DecimalField(decimal_places=2, max_digits=6)
    listing_detail = models.TextField(max_length=800)
    listing_category = models.TextField(max_length=30, null=True)
    image_path = models.TextField(max_length=500, null=True)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    end_date = models.DateField(null=True, default=datetime.date.today)

class Bids(models.Model):
    bid_amount = models.DecimalField(decimal_places=2, max_digits=6 ) 
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
class AuctionListingComments(models.Model):
    comment = models.TextField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    