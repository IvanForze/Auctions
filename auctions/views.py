from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.storage import default_storage
import os
from .models import User, Listing, Comment, Category

def check_session(request):
    if request.user.is_authenticated:
        return True
    else:
        return False
    
@login_required(login_url='login')
def upload(request):
    if request.method == 'POST' and request.FILES:
        # Получаем данные из формы
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = float(request.POST.get('price').replace(",", "."))
        categoryName = request.POST.get('category')
        category = Category.objects.filter(categoryName = categoryName).first()

        if not category:
            category = Category.objects.create(
                categoryName = categoryName
            )
        print(price)
        image_file = request.FILES['image']

        # Сохраняем файл
        file_name = default_storage.save(os.path.join('uploads', image_file.name), image_file)
        print(file_name)
        file_url = default_storage.url(file_name)

        # Сохраняем в базу данных
        Listing.objects.create(
            title=title,
            description=description,
            owner = request.user,
            category = category,
            price=price,
            image=file_name
        )
        return HttpResponseRedirect(reverse("index"))

def listing_page(request, id):
    listing = Listing.objects.filter(id = id).first()
    comments = Comment.objects.filter(listing = listing).order_by('-date')
    print(listing)
    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "comments": comments
    })

@login_required(login_url='login')
def add_comment(request, id):
    listing = Listing.objects.filter(id = id).first()

    text = request.POST.get('comment')
    Comment.objects.create(
        listing = listing,
        user = request.user,
        text = text
    )

    return redirect("listing_page", id=id)

@login_required(login_url='login')
def add_watchlist(request, id):
    url = request.META.get('HTTP_REFERER')
    listing = Listing.objects.filter(id = id).first()
    if request.user not in listing.watchlist.all():
        listing.watchlist.add(request.user)
    else:
        listing.watchlist.remove(request.user)
    print(url)
    return redirect(url)

@login_required(login_url='login')
def bid(request, id):
    listing = Listing.objects.filter(id = id).first()
    comments = Comment.objects.filter(listing = listing).order_by('-date')

    if not listing:
        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "comments": comments,
            "message": "This listing doesn't exist",
            "success": False
        })

    try:
        bid_price = float(request.POST.get('bid-price').replace(",", "."))
    except ValueError:
        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "comments": comments,
            "message": "Invalid price",
            "success": False
        })

    if listing.price < bid_price:
        listing.price = bid_price
    else:
        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "comments": comments,
            "message": "You must bid higher amount!",
            "success": False
        })

    listing.save()
    return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "comments": comments,
            "message": "Your bid was placed!",
            "success": True
        })

@login_required(login_url='login')
def watchlist(request):
    listings = Listing.objects.all().filter(watchlist = request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })

@login_required(login_url='login')
def create(request):
    return render(request, "auctions/create.html")

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
