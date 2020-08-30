from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from auctions.forms import NewListingForm, SubmitBidForm, AuctionListingCommentForm
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
    susername = Bids.objects.get(auction_listing=Auction_object, is_highest_bid=True).user.username
    if susername == Auction_object.user.username:
        remove_auction(request, plisting)
    
    Auction_object.active = False
    Auction_object.save()
    vuser = get_object_or_404(User, username=susername)
    FinishedAuctions.objects.create(winner=vuser, listing_name=Auction_object)
    return redirect('index')

def remove_auction(request, plisting):
    auction = AuctionListing.objects.get(listing_name=plisting)
    auction.delete()
    return users_view(request)

def created_auctions_view(request):
    created_auctions = {}
    head = "Your Created Auctions"
    try:
        susername = request.session.get("uname", "")
        vuser = get_object_or_404(User, username=susername)
    except:
        head = "invalid user"           
    try:
        created_auctions = AuctionListing.objects.filter(user=vuser)        
    except:
        head = "No auctions to display" 
    return render(request, "auctions/index.html", {
        "auctions" : created_auctions,
        "heading" : head })
        
def users_view(request):
    try:
        susername = request.session.get("uname", "")
        vuser = get_object_or_404(User, username=susername)
    except:
        auction_data = "invalid user"        
    
    auctions_won_list = []    
    try:
        auction_data = FinishedAuctions.objects.filter(winner=vuser) 
        for ad in auction_data:
            auctions_won_list.append(ad.listing_name)
    except:
        auction_data = "No auctions to display" 
    
    auctions_watchlisted = []    
    try:
        watchlist_data = WatchList.objects.filter(user=vuser) 
        for wd in watchlist_data:
            auctions_watchlisted.append(wd.auction_listing)
    except:
        watchlist_data = "No auctions to display" 
    
    auction_bids = []    
    try:
        active_bid_data = Bids.objects.filter(user=vuser) 
        for abd in watchlist_data:
            auction_bids.append(abd.auction_listing)
    except:
        active_bid_data = "No auctions to display" 
    if auctions_won_list is not None:
        won = True
    else:
        won = False
    return render(request, "auctions/index.html", {
        "auctions" : auctions_won_list,
        "won" : won,
        "watchlisted" : auctions_watchlisted,
        "active_bids" : auction_bids,
        "heading" : 'Your Auctions'})
            
def watchlist(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)    
    try:
        User_object = get_object_or_404(User, username=request.session.get("uname", ""))
    except:
        return show_listing(request, Auction_object)
    try:
        #it is currently watchlisted, we are removing it
        wl = WatchList.objects.get(auction_listing=Auction_object, user=User_object)
        wl.delete()
    except:
        #not yet watchlisted - we are adding it
        WatchList.objects.create(auction_listing=Auction_object, user=User_object)        
    return show_listing(request, Auction_object)

def add_comments(request, plisting):
    Auction_object = get_object_or_404(AuctionListing, listing_name=plisting)
    vcomments = request.POST.get("listing_comments")
    susername = request.session.get("uname", "")
    vuser = User.objects.get(username=susername)
    AuctionListingComments.objects.create(
        listing=Auction_object,
        comment=vcomments,
        user=vuser)
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
            user=vuser)
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
    # user_case = listing.user
    # username_case = user_case.username
    vbid_form = SubmitBidForm()
    vcomment_form = AuctionListingCommentForm() 
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
            is_highest_bid=True)
        vcurrent_bid = Bid_Object.bid_amount
        vhighest_bidder = Bid_Object.user
    except:
        vcurrent_bid = listing.listing_price
        vhighest_bidder = ""
        
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
        "dhighest_bidder" : vhighest_bidder,
        "msg" : optional_msg,
        "dcomment_form" : vcomment_form,
        "dcomments" : AuctionListingComments.objects.all()
        })
    
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

