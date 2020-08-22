from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from auctions.forms import NewListingForm

from .models import User, AuctionListing, Bids, AuctionListingComments


def index(request):
    auctions = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auctions" : auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
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
#AggregateStats.objects.create(owning_user=v_user)

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
            puser = request.POST.get("huser")
            usey = User.objects.get(username=puser)
        
            Auction_object = get_object_or_404(AuctionListing, listing_name=vname)
            if not Auction_object:
                AuctionListing.objects.create(
                    listing_name=vname, 
                    listing_price=vlisting_price, 
                    listing_detail=vlisting_detail,
                    image_path = vimage_path,
                    listing_category = vlisting_category,
                    end_date = vend_date,
                    user=usey
            )
            
            vimg_width = "0"
            vimg_height = "0"            
            if vimage_path:
                vimg_width = "400"
                vimg_height = "500" 
            
            category_text = ""
            if vlisting_category:              
                category_text = "Listing Category: " + vlisting_category
            
            return render(request, "auctions/display_listing.html", {
                "dlisting_name" : vname,
                "dcurrent_bid" : vlisting_price,
                "dimage_path" : vimage_path,
                "duser_name" : usey.username,
                "duser_email" : usey.email,
                "dlisting_category" : category_text,
                "dlisting_detail" : vlisting_detail,
                "dimg_width" : vimg_width,
                "dimg_height" : vimg_height,
                "dend_date" : vend_date,
            })
        
    listing_form = NewListingForm()
    
    return render(request, "auctions/create_listing.html", {
        "d_form" : listing_form,
    })

