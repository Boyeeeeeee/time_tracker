import os.path
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import GoalForm, WishForm
from .models import Goal, Wish,TimeAllocation
from .algorithms import allocate_time
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define SCOPES
SCOPES = ['https://www.googleapis.com/auth/calendar']

import os

def get_credentials(user):
    creds = None
    token_dir = 'tokens'
    token_file = f'{token_dir}/token_{user.id}.json'  # Store user-specific credentials

    # Create the tokens directory if it doesn't exist
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds



@login_required
def sync_with_google_calendar(request):
    creds = get_credentials(request.user)  # Fetch credentials for the logged-in user
    service = build('calendar', 'v3', credentials=creds)
    
    try:
        # List upcoming 10 events from the user's calendar
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
    except HttpError as error:
        print(f'An error occurred: {error}')
        events = []

    return render(request, 'core/calendar.html', {'events': events})


def home(request):
    return render(request, 'core/base.html')


@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')  # Redirect to dashboard or wherever you need
    else:
        form = GoalForm()
    return render(request, 'core/add_goal.html', {'form': form})

@login_required
def add_wish(request):
    if request.method == 'POST':
        form = WishForm(request.POST)
        if form.is_valid():
            wish = form.save(commit=False)
            wish.user = request.user
            wish.save()
            return redirect('dashboard')  # Redirect to dashboard or wherever you need
    else:
        form = WishForm()
    return render(request, 'core/add_wish.html', {'form': form})

@login_required
def dashboard(request):
    # Fetch the logged-in user's goals and wishes
    goals = Goal.objects.filter(user=request.user)
    wishes = Wish.objects.filter(user=request.user)

    context = {
        'goals': goals,
        'wishes': wishes
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def update_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'core/update_goal.html', {'form': form})

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('dashboard')
    return render(request, 'core/delete_goal.html', {'goal': goal})


@login_required
def update_wish(request, pk):
    wish = get_object_or_404(Wish, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WishForm(request.POST, instance=wish)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = WishForm(instance=wish)
    return render(request, 'core/update_wish.html', {'form': form})


@login_required
def delete_wish(request, pk):
    wish = get_object_or_404(Wish, pk=pk, user=request.user)
    if request.method == 'POST':
        wish.delete()
        return redirect('dashboard')
    return render(request, 'core/delete_wish.html', {'wish': wish})





@login_required
def allocate_time(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    previous_allocation = TimeAllocation.objects.filter(goal=goal).first()

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            start_time_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            end_time_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        except ValueError as e:
            print(f'Error parsing time: {e}')
            return redirect('allocate_time', goal_id=goal_id)

        start_time_aware = timezone.make_aware(start_time_dt, timezone.get_current_timezone())
        end_time_aware = timezone.make_aware(end_time_dt, timezone.get_current_timezone())

        creds = get_credentials(request.user)  # Fetch credentials for the logged-in user
        service = build('calendar', 'v3', credentials=creds)

        if previous_allocation:
            previous_allocation.start_time = start_time_aware
            previous_allocation.end_time = end_time_aware

            # Update the event in Google Calendar
            event_id = previous_allocation.google_calendar_event_id
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            event['start']['dateTime'] = start_time_aware.isoformat()
            event['end']['dateTime'] = end_time_aware.isoformat()

            service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            previous_allocation.save()

        else:
            # Create a new event
            event = {
                'summary': goal.title,
                'start': {
                    'dateTime': start_time_aware.isoformat(),
                    'timeZone': 'Africa/Lagos',
                },
                'end': {
                    'dateTime': end_time_aware.isoformat(),
                    'timeZone': 'Africa/Lagos',
                },
            }

            event = service.events().insert(calendarId='primary', body=event).execute()

            # Save the new allocation with the Google Calendar event ID
            TimeAllocation.objects.create(
                user=request.user,
                goal=goal,
                start_time=start_time_aware,
                end_time=end_time_aware,
                google_calendar_event_id=event['id']  # Save event ID
            )

        return redirect('allocated_times')

    return render(request, 'core/allocate_time.html', {
        'goal': goal,
        'previous_allocation': previous_allocation
    })


@login_required
def allocated_times(request):
    allocations = TimeAllocation.objects.filter(user=request.user).order_by('start_time')
    return render(request, 'core/allocated_times.html', {'allocations': allocations})

@login_required
def delete_allocation(request, allocation_id):
    allocation = get_object_or_404(TimeAllocation, id=allocation_id, user=request.user)

    if request.method == 'POST':
        creds = get_credentials(request.user)  # Fetch credentials for the logged-in user
        service = build('calendar', 'v3', credentials=creds)

        # Delete the event from Google Calendar
        if allocation.google_calendar_event_id:
            try:
                service.events().delete(calendarId='primary', eventId=allocation.google_calendar_event_id).execute()
                print(f"Deleted event {allocation.google_calendar_event_id} from Google Calendar")
            except HttpError as error:
                print(f'An error occurred while deleting from Google Calendar: {error}')
                # Optional: Return an error message or feedback to the user
                return redirect('allocated_times', error='Google Calendar event deletion failed.')

        # After successfully deleting from Google Calendar, delete from the database
        allocation.delete()
        print(f"Deleted allocation {allocation_id} from the database")

    return redirect('allocated_times')


