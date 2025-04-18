from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Score
import random
import requests

# User registration view
def register(request):
    """
    Handle user registration.
    - On GET, display the registration form.
    - On POST, validate the form, create the user, log them in, and redirect to home.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the user
            login(request, user)  # Log the user in immediately after registration
            return redirect('home')  # Redirect to the home page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# User login view
def login_view(request):
    """
    Handle user login.
    - On GET, display the login form.
    - On POST, validate the login form, log the user in, and redirect to home.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Home view with user session management
def home(request):
    """
    Handle the home page, where the user enters their name to start the quiz.
    If the user is logged in, use their username.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username  # Access the authenticated user's username
        else:
            username = request.POST.get('username')  # Default to POSTed username if not logged in
        request.session['username'] = username
        request.session['questions'] = get_questions()  # Fetch quiz questions from API
        request.session['score'] = 0
        return redirect('quiz', q_num=0)
    return render(request, 'home.html')

# Quiz view (Only accessible to authenticated users)
@login_required
def quiz(request, q_num):
    """
    Display the quiz questions and options.
    Only authenticated users can access this view.
    """
    if q_num >= len(request.session['questions']):
        return redirect('result')

    question = request.session['questions'][q_num]
    options = question['incorrect_answers'] + [question['correct_answer']]
    random.shuffle(options)

    if request.method == 'POST':
        if request.POST.get('option') == question['correct_answer']:
            request.session['score'] += 1
        return redirect('quiz', q_num=q_num + 1)

    return render(request, 'quiz.html', {'q_num': q_num, 'question': question, 'options': options})

# Result view (Show the user’s score and store it in the database)
@login_required
def result(request):
    """
    Display the result of the quiz, store the score in the database, and show the user's score.
    """
    username = request.session.get('username', 'Guest')
    score = request.session.get('score', 0)

    # Store the user's score in the database
    Score.objects.create(name=username, score=score)

    return render(request, 'result.html', {'username': username, 'score': score})

# Utility function to fetch quiz questions from an API
def get_questions(amount=5, category=9, difficulty='medium'):
    url = f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type=multiple'
    response = requests.get(url)
    return response.json().get('results', [])
