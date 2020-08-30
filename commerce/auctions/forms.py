from django import forms
import datetime

class NewListingForm(forms.Form):
    listing_name = forms.CharField(label='Name', max_length=30)
    listing_price = forms.DecimalField(decimal_places=2, max_digits=9)
    listing_detail = forms.CharField(widget=forms.Textarea, max_length=800)
    listing_category = forms.CharField(label='Category', max_length=30, required=False)
    image_path = forms.CharField(max_length=500, required=False)
    end_date = forms.DateField(initial=datetime.date.today() + datetime.timedelta(7))
    
class SubmitBidForm(forms.Form):
    bid = forms.DecimalField(decimal_places=2, max_digits=9)
    
class AuctionListingCommentForm(forms.Form):
     listing_comments = forms.CharField(widget=forms.Textarea, label='', max_length=1000)