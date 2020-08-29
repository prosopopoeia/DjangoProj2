from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from auctions.forms import NewListingForm, SubmitBidForm
from decimal import *

from .models import User, AuctionListing, Bids, AuctionListingComments, WatchList, FinishedAuctions
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["uname"] = username
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"] 
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        request.session["uname"] = username
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
            ###################################################
            # new_entry = Entry()
            # new_entry.cat = v_this_category_this_period
            # new_entry.entry_note = e_notes
            # new_entry.amount = decimal.Decimal(e_amt)
            # new_entry.save()   
            ###################################################

###################################################################################
def index(request):
    auctions = AuctionListing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "auctions" : auctions,
        "heading" : "Active Listings"})

def end_auction(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)
    Auction_object.active = False
    Auction_object.save()
    try:
        susername = Bids.objects.get(auction_listing=Auction_object, is_highest_bid=True).user.username
    except:
        Auction_object.delete()
        return HttpResponse("fail")
    vuser = get_object_or_404(User, username=susername)
    FinishedAuctions.objects.create(winner=vuser, listing_name=Auction_object)
    return redirect('index')

def remove_auction(request, plisting):
    auction = AuctionListing.objects.get(listing_name=plisting)
    auction.delete() 
    return won_view(request)

def won_view(request):
    try:
        susername = request.session.get("uname", "")
        vuser = get_object_or_404(User, username=susername)
    except:
        auction_data = "invalid user"        
    auction_list = []    
    try:
        auction_data = FinishedAuctions.objects.filter(winner=vuser) 
        for ad in auction_data:
            auction_list.append(ad.listing_name)
    except:
        auction_data = "No auctions to display"             
    return render(request, "auctions/index.html", {
        "auctions" : auction_list,
        "heading" : 'Your Winning Auctions'})
            
def watchlist(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)    
    try:
        User_object = get_object_or_404(User, username=request.session.get("uname", ""))
    except:
        #not logged in
        return show_listing(request, Auction_object)
    try:
        wl = WatchList.objects.get(auction_listing=Auction_object, user=User_object)
        wl.delete()
    except:
        #not yet watchlisted
        WatchList.objects.create(auction_listing=Auction_object, user=User_object)        
    return show_listing(request, Auction_object)

def display_listing(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)
    return show_listing(request, Auction_object)

def bid(request, plisting):
    vbid_amount = Decimal(request.POST.get("bid"))
    listing = get_object_or_404(AuctionListing, listing_name=plisting)        
    try:        
        susername = request.session.get("uname", "")
        vuser = User.objects.get(username=susername)
        vbid = Bids.objects.get(
            auction_listing=listing,
            is_highest_bid=True)        
    except:
        #return show_listing(request, listing)
        return render(request, "auctions/display_listing.html", {
            "dlisting_name" : listing.listing_name,
            "dcurrent_bid" : listing.listing_price,
            "dimage_path" : listing.image_path,
            "duser_name" : listing.user.username,
            "duser_email" : listing.user.email,
            "dlisting_category" : "none",
            "dlisting_detail" : listing.listing_detail,
            "dimg_width" : "0",
            "dimg_height" : "0",
            "dend_date" : listing.end_date,
            "watchlist_state" : "no user: " + request.session.get("uname", "") + " , or perhaps no bid. from post: " + str(vbid_amount) + " current highest: "})   
    msg = ""
    if vbid_amount > vbid.bid_amount:
        Bids.objects.create(
            bid_amount=vbid_amount, 
            is_highest_bid=True,
            auction_listing=listing,
            user=vuser
        )
        vbid.is_highest_bid = False
        vbid.save()
        listing.listing_price = vbid_amount
        listing.save()
    else:
        msg = "Error - Bid must exceed current bid!"
    return show_listing(request, listing, msg)    
    
def show_listing(request, listing, optional_msg=""):
    vimg_width = "0"
    vimg_height = "0"            
    if listing.image_path:
        vimg_width = "400"
        vimg_height = "500"     
    if listing.active == False:
        return redirect('index')
    vbid_form = SubmitBidForm()         
    try:        
        susername = request.session.get("uname", "")
        vuser = User.objects.get(username=susername)
    except:
        return render(request, "auctions/display_listing.html", {
            "dlisting_name" : listing.listing_name,
            "dcurrent_bid" : listing.listing_price,
            "dimage_path" : listing.image_path,
            "duser_name" : listing.user.username,
            "duser_email" : listing.user.email,
            "dlisting_category" : listing.listing_category,
            "dlisting_detail" : listing.listing_detail,
            "dimg_width" : vimg_width,
            "dimg_height" : vimg_height,
            "dend_date" : listing.end_date,
            "watchlist_state" : "",
            "dbid_form" : vbid_form,
            "msg" : optional_msg,})    
    try:
        Bid_Object = Bids.objects.get(
            auction_listing=listing,
            is_highest_bid=Yes)
        vcurrent_bid = Bid_Object.bid_amount
    except:
        vcurrent_bid = listing.listing_price
        
    watchstate = "Remove from watchlist"    
    try:
        Watchlist_object = WatchList.objects.get(
            auction_listing=listing,
            user=vuser)            
    except: 
        watchstate = "Add to watchlist"    
    return render(request, "auctions/display_listing.html", {
        "dlisting_name" : listing.listing_name,
        "dcurrent_bid" : vcurrent_bid,
        "dimage_path" : listing.image_path,
        "duser_name" : listing.user.username,
        "duser_email" : listing.user.email,
        "dlisting_category" : listing.listing_category,
        "dlisting_detail" : listing.listing_detail,
        "dimg_width" : vimg_width,
        "dimg_height" : vimg_height,
        "dend_date" : listing.end_date,
        "watchlist_state" : watchstate,
        "dbid_form" : vbid_form,
        "msg" : optional_msg,})
    
def end_auction(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)
    Auction_object.active = False
    Auction_object.save()
    susername = Bids.objects.get(auction_listing=Auction_object, is_highest_bid=True).user.username
    vuser = get_object_or_404(User, username=susername)
    FinishedAuctions.objects.create(winner=vuser, listing_name=Auction_object)
    return redirect('index')

def create_listing(request):
    if request.method == "POST":
        vcreate_listing_form = NewListingForm(request.POST)
        
        if vcreate_listing_form.is_valid():
            vname = vcreate_listing_form.cleaned_data["listing_name"]
            vlisting_price =  vcreate_listing_form.cleaned_data["listing_price"]
            vlisting_detail  = vcreate_listing_form.cleaned_data["listing_detail"]
            vimage_path  = vcreate_listing_form.cleaned_data["image_path"]
            vlisting_category = vcreate_listing_form.cleaned_data["listing_category"]
            vend_date = vcreate_listing_form.cleaned_data["end_date"]
            puser = request.POST.get("huser") #TODO - TEST request.session.get("uname")!!!!!!!!******!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!*******
            vuser = User.objects.get(username=puser)        
            try:
                Auction_object = AuctionListing.objects.get(listing_name=vname)
            except ObjectDoesNotExist:
                AuctionListing.objects.create(
                    listing_name=vname, 
                    listing_price=vlisting_price, 
                    listing_detail=vlisting_detail,
                    image_path = vimage_path,
                    listing_category = vlisting_category,
                    end_date = vend_date,
                    user=vuser)                
                Auction_object = get_object_or_404(AuctionListing, listing_name=vname)
                Bids.objects.create(
                    bid_amount=vlisting_price,
                    auction_listing=Auction_object,
                    is_highest_bid=True,
                    user = vuser)
            return show_listing(request, Auction_object)
            
    listing_form = NewListingForm()    
    return render(request, "auctions/create_listing.html", {"d_form" : listing_form})

