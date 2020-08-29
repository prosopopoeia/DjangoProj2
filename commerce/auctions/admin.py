from django.contrib import admin

from .models import User, AuctionListing, Bids, AuctionListingComments, WatchList, FinishedAuctions

admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bids)
admin.site.register(AuctionListingComments)
admin.site.register(WatchList)
admin.site.register(FinishedAuctions)
