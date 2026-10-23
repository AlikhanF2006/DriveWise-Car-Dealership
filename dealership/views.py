"""Working Django pages and session-authenticated JSON endpoints."""
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from .forms import RegistrationForm, ReviewForm
from .models import Dealer, Review, CarMake


def dealer_data(dealer):
    return {
        'id': dealer.pk, 'name': dealer.name, 'address': dealer.address,
        'city': dealer.city, 'state': dealer.state, 'zipcode': dealer.zipcode,
        'phone': dealer.phone, 'description': dealer.description,
    }


def review_data(item):
    return {
        'id': item.pk, 'dealer_id': item.dealer_id, 'user': item.author.username,
        'rating': item.rating, 'review': item.review, 'created_at': item.created_at.isoformat(),
    }


def error(message, code=400):
    return JsonResponse({'error': message}, status=code)


def json_body(request):
    try:
        obj = json.loads(request.body.decode('utf-8') or '{}')
        return obj if isinstance(obj, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def home(request):
    state = request.GET.get('state', '').upper().strip()
    dealers = Dealer.objects.all().order_by('name')
    if state:
        dealers = dealers.filter(state=state)
    states = Dealer.objects.values_list('state', flat=True).distinct().order_by('state')
    return render(request, 'dealership/home.html', {'dealers': dealers, 'states': states, 'chosen_state': state})


def home_by_state(request, state):
    return redirect(f'/?state={state.upper()}')


def dealer_detail(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    reviews = dealer.reviews.select_related('author')
    return render(request, 'dealership/dealer.html', {'dealer': dealer, 'reviews': reviews})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Welcome back!')
        return redirect('home')
    return render(request, 'dealership/login.html', {'form': form})


@require_POST
def logout_page(request):
    logout(request)
    messages.info(request, 'You have signed out.')
    return redirect('home')


def register_page(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('home')
    return render(request, 'dealership/register.html', {'form': form})


@login_required
def review_form(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.dealer = dealer
        review.save()
        messages.success(request, 'Your review has been published.')
        return redirect('dealer_detail', dealer_id=dealer.pk)
    return render(request, 'dealership/review_form.html', {'form': form, 'dealer': dealer})


@require_GET
def api_dealers(request):
    return JsonResponse({'dealerships': [dealer_data(d) for d in Dealer.objects.all().order_by('id')]})


@require_GET
def api_dealers_by_state(request, state):
    return JsonResponse({'state': state.upper(), 'dealerships': [dealer_data(d) for d in Dealer.objects.filter(state__iexact=state).order_by('id')]})


@require_GET
def api_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    result = dealer_data(dealer)
    result['reviews'] = [review_data(r) for r in dealer.reviews.select_related('author')]
    return JsonResponse(result)


@require_GET
def api_dealer_reviews(request, dealer_id):
    get_object_or_404(Dealer, pk=dealer_id)
    reviews = Review.objects.filter(dealer_id=dealer_id).select_related('author')
    return JsonResponse({'dealer_id': dealer_id, 'reviews': [review_data(r) for r in reviews]})


@require_POST
def api_add_review(request):
    if not request.user.is_authenticated:
        return error('Sign in before posting a review.', 401)
    data = json_body(request)
    try:
        dealer_id = int(data.get('dealer_id', 0))
        rating = int(data.get('rating', 0))
    except (ValueError, TypeError):
        return error('dealer_id and rating must be numbers.')
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    review_text = str(data.get('review', '')).strip()
    if rating not in range(1, 6) or not (3 <= len(review_text) <= 2000):
        return error('Rating must be 1–5 and review length must be 3–2000.')
    created = Review.objects.create(dealer=dealer, author=request.user, rating=rating, review=review_text)
    return JsonResponse(review_data(created), status=201)


@require_GET
def api_car_makes(request):
    makes = CarMake.objects.prefetch_related('models').order_by('name')
    return JsonResponse({'car_makes': [
        {'id': make.id, 'name': make.name, 'models': [{'id': m.id, 'name': m.name} for m in make.models.all()]}
        for make in makes
    ]})


POSITIVE = {'fantastic', 'amazing', 'great', 'excellent', 'friendly', 'good', 'love', 'perfect', 'helpful', 'фантастические', 'отлично', 'хорошо'}
NEGATIVE = {'bad', 'terrible', 'awful', 'poor', 'rude', 'worst', 'broken', 'disappointing', 'плохо', 'ужасно'}


def classify_sentiment(value):
    """Small demonstrative keyword classifier, not a trained ML model."""
    tokens = {t.strip('.,!?;:\"\'()[]') for t in value.lower().split()}
    score = len(tokens & POSITIVE) - len(tokens & NEGATIVE)
    return 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'


def api_sentiment(request):
    if request.method not in ('GET', 'POST'):
        return error('Use GET or POST.', 405)
    data = json_body(request) if request.method == 'POST' else request.GET
    text = str(data.get('text', data.get('review', ''))).strip()
    if not text:
        return error('Provide text or review.')
    return JsonResponse({'text': text, 'sentiment': classify_sentiment(text), 'method': 'keyword demo'})


@require_GET
def api_csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_GET
def api_me(request):
    return JsonResponse({'authenticated': request.user.is_authenticated, 'username': request.user.username if request.user.is_authenticated else None})


@require_POST
def api_login(request):
    data = json_body(request)
    user = authenticate(request, username=str(data.get('username', '')), password=str(data.get('password', '')))
    if user is None:
        return error('Invalid username or password.', 401)
    login(request, user)
    return JsonResponse({'authenticated': True, 'username': user.username})


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'authenticated': False, 'message': 'Signed out successfully.'})


@require_POST
def api_register(request):
    data = json_body(request)
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', ''))
    form = RegistrationForm({
        'username': username,
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'email': email,
        'password1': password,
        'password2': password,
    })
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
    try:
        user = form.save()
    except IntegrityError:
        return error('Username already exists.')
    login(request, user)
    return JsonResponse({'registered': True, 'username': user.username}, status=201)
