from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'Invalid username or password.'
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.info('New user')
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'User already exists.'
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        # url = "https://willow15liu-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership"
        url = "https://willow15liu-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context['dealership_list'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        context = {}
        # url = 'https://willow15liu-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review'
        url = 'https://willow15liu-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review'
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # review_contents = ' '.join([review.review + '->' + review.sentiment for review in reviews])
        # return HttpResponse(review_contents)
        url = "https://willow15liu-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url, dealerId=dealer_id)

        context['review_list'] = reviews
        context['dealer_id'] = dealer_id
        context['dealership_name'] = dealerships[0].full_name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            context = {}
            context['dealer_id'] = dealer_id

            cars = CarModel.objects.filter(dealership=dealer_id)
            context['cars'] = cars

            url = "https://willow15liu-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//api/dealership"
            dealerships = get_dealers_from_cf(url, dealerId=dealer_id)
            context['dealership_name'] = dealerships[0].full_name

            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == 'POST':
            print(request.POST)

            # post_body = json.loads(request.body)
            review = dict()
            review['time'] = datetime.utcnow().isoformat()
            review['id'] = int(datetime.utcnow().timestamp())
            review['name'] = user.username
            review['dealership'] = dealer_id
            review['review'] = request.POST['content']
            if 'purchasecheck' in request.POST and request.POST['purchasecheck'] == 'on':
                review['purchase'] = True
            else:
                review['purchase'] = False
            review['purchase_date'] = request.POST['purchasedate']
            car = CarModel.objects.get(pk=request.POST['car'])
            review['car_make'] = car.car_make.name
            review['car_model'] = car.name
            review['car_year'] = car.year.strftime('%Y')

            json_payload = {'review': review}

            url = 'https://willow15liu-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review'
            response = post_request(url, json_payload)
            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
