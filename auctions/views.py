from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from .models import User, Category, Bid, Listing, Comment


def index(request):
    context = {'listings' : Listing.objects.filter(activity=True).all()}
    return render(request, "auctions/index.html", context)

def listing_page(request, listing_id):
    if request.method == 'POST':
        if 'add-to-watchlist' in request.POST:
            listing = Listing.objects.get(pk=listing_id)
            current_user = request.user
            listing.watchers.add(current_user)
            listing.save()

            context = {'listings' : Listing.objects.filter(activity=True).all(),
                        'success_message' : 'Listing added to your Watchlist!'}
            return render(request, "auctions/index.html", context)

        if 'bid-on-item' in request.POST:
            listing = Listing.objects.get(pk=listing_id)
            bid = int(request.POST['bid'])

            if bid < listing.starting_bid or bid <= listing.current_price:
                error_message = 'Wrong value! The bid must be at least as large as the starting bid, and must be greater than any other bids.'
                success_message = None
            else:
                new_bid = Bid.objects.create(author=request.user, value=bid)
                new_bid.save()
                listing.bids.add(new_bid)
                listing.save()

                success_message = 'You succesfully placed bid on this item!'
                error_message = None
                
            try:
                current_winner = listing.bids.last().author
            except AttributeError:
                current_winner = None
            context = {'listing': listing,
            'length_bids': len(listing.bids.all()),
            'current_winner': current_winner,
            'comments':Comment.objects.filter(listing=listing).all()
            }
            if success_message is not None:
                context['success_message'] = success_message
            elif error_message is not None:
                context['error_message'] = error_message
            return render(request, "auctions/listing_page.html", context)

        if 'close' in request.POST:
            listing = Listing.objects.get(pk=listing_id)
            listing.activity = False
            winner = listing.bids.last().author
            listing.winner = winner
            listing.save()

            try:
                current_winner = listing.bids.last().author
            except AttributeError:
                current_winner = None

            context = {'listing': listing,
            'length_bids': len(listing.bids.all()),
            'current_winner': current_winner,
            'comments':Comment.objects.filter(listing=listing).all()
            }
            return render(request, "auctions/listing_page.html", context)
        
        if 'add-comment' in request.POST:
            content = request.POST.get('comment-content', False)
            listing = Listing.objects.get(pk=listing_id)
            author = request.user
            
            new_comment = Comment.objects.create(
                author=author,
                content = content,
                listing = listing)
            new_comment.save()

            success_message = 'Comment added!'
            try:
                current_winner = listing.bids.last().author
            except AttributeError:
                current_winner = None
                
            context = {'listing': listing,
            'length_bids': len(listing.bids.all()),
            'current_winner': current_winner,
            'success_message': success_message,
            'comments':Comment.objects.filter(listing=listing).all()
            }
            return render(request, "auctions/listing_page.html", context)
    else:
        listing = Listing.objects.get(pk=listing_id)
        try:
            current_winner = listing.bids.last().author
        except AttributeError:
            current_winner = None
        
        comments = Comment.objects.filter(listing=listing).all()
        if len(comments) == 0:
            comments = None
        context = {'listing': listing,
        'length_bids': len(listing.bids.all()),
        'current_winner': current_winner,
        'comments':comments
        }
        return render(request, "auctions/listing_page.html", context)

def category_page(request, category_id):
    if category_id == 0:
        category = None
    else:
        category = Category.objects.get(pk=category_id)
    context = {'category': category, 'listings':Listing.objects.filter(category=category, activity=True).all()}
    return render(request, "auctions/category_page.html", context)


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
                "error_message": "Invalid username and/or password."
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
                "error_message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "error_message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        category = Category.objects.get(pk=request.POST['category'])
        picture_url = request.POST['picture_url']
        author = request.user
        try:
            listing = Listing.objects.create(
                author=author,
                title=title,
                description=description,
                category=category,
                picture_url=picture_url,
                starting_bid=starting_bid
            )
            listing.save()
            success_messages.success(request, 'Listing saved!')
            return HttpResponseRedirect(reverse("index"))
        except:
            context = {
                'error_message':'There was an issue creating this listing.',
                'categories' : Category.objects.all()
            }
            return render(request, "auctions/create.html", context)

    else:
        context = {'categories' : Category.objects.all()}
        return render(request, "auctions/create.html", context)

def categories(request):
    context = {'categories' : Category.objects.all()}
    return render(request, "auctions/categories.html", context)

@login_required
def watchlist(request):
    user = request.user
    watched_listings = user.watched_listings.all()
    return render(request, "auctions/watchlist.html", {
        'watched_listings':watched_listings
    })

