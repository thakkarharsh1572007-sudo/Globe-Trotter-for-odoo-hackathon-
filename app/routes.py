from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from datetime import datetime
from datetime import datetime
from app.models import User, Trip, Stop, Activity , ChecklistItem ,TripNote ,TripPhoto, TripParticipant
from app.models import Trip

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)
@auth.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If the user submits the form
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if a user with this email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Please log in.')
            return redirect(url_for('auth.signup'))

        # Create new user and hash the password
        new_user = User(email=email, username=username)
        new_user.set_password(password)

        # Add to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))

    # If it's a GET request, just show the signup page
    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('auth.dashboard')) # Redirect to their trips
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@login_required
def dashboard():
    # Fetch all trips created by the currently logged-in user
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', trips=user_trips)

@auth.route('/create-trip', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        # Convert the string dates from the HTML form into Python Date objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Create the new trip in the database
        new_trip = Trip(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id
        )
        db.session.add(new_trip)
        db.session.commit()

        flash('Trip created successfully!')
        return redirect(url_for('auth.dashboard'))

    return render_template('create_trip.html')
@auth.route('/trip/<int:trip_id>')
@login_required
def trip_view(trip_id):
    # Fetch the trip and ensure the current user owns it
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash("You don't have permission to view this trip.", "danger")
        return redirect(url_for('auth.dashboard'))
    
    # Fetch all stops for this trip, ordered by arrival date
    stops = Stop.query.filter_by(trip_id=trip.id).order_by(Stop.arrival_date).all()
    
    return render_template('trip_view.html', trip=trip, stops=stops)


@auth.route('/trip/<int:trip_id>/add-stop', methods=['POST'])
@login_required
def add_stop(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
        
    city_name = request.form.get('city_name')
    arrival_date_str = request.form.get('arrival_date')
    departure_date_str = request.form.get('departure_date')
    
    # Convert HTML string dates to Python dates
    arrival_date = datetime.strptime(arrival_date_str, '%Y-%m-%d').date()
    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
    
    # Create and save the new stop
    new_stop = Stop(
        trip_id=trip.id,
        city_name=city_name,
        arrival_date=arrival_date,
        departure_date=departure_date
    )
    existing_stop = Stop.query.filter(Stop.trip_id == trip.id, Stop.city_name.ilike(city_name)).first()
    
    if existing_stop:
        flash(f'You already have {city_name} in your itinerary!', 'warning')
        return redirect(url_for('auth.trip_view', trip_id=trip.id))
    db.session.add(new_stop)
    db.session.commit()
    
    flash(f'{city_name} added to your itinerary!')
    return redirect(url_for('auth.trip_view', trip_id=trip.id))
@auth.route('/stop/<int:stop_id>/add-activity', methods=['GET', 'POST'])
@login_required
def add_activity(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    
    # Security: Make sure the user owns the trip this stop belongs to
    if stop.trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        cost = float(request.form.get('cost') or 0.0)
        date_str = request.form.get('activity_date')
        
        activity_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_activity = Activity(
            stop_id=stop.id,
            name=name,
            cost=cost,
            activity_date=activity_date
        )
        db.session.add(new_activity)
        db.session.commit()
        
        flash(f'Activity added to {stop.city_name}!')
        return redirect(url_for('auth.trip_view', trip_id=stop.trip_id))

    return render_template('add_activity.html', stop=stop)
@auth.route('/trip/<int:trip_id>/budget')
@login_required
def trip_budget(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    # Security check
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))

    total_cost = 0
    city_costs = {}
    labels = []
    values = []

    # Calculate costs per stop
    for stop in trip.stops:
        stop_cost = sum(activity.cost for activity in stop.activities)
        if stop_cost > 0:
            city_costs[stop.city_name] = stop_cost
            labels.append(stop.city_name)
            values.append(stop_cost)
            total_cost += stop_cost

    return render_template(
        'budget.html', 
        trip=trip, 
        total_cost=total_cost, 
        labels=labels, 
        values=values
    )
@auth.route('/share/<int:trip_id>')
def share_trip(trip_id):
    # Fetch the trip, but we don't check if the user owns it because it's public
    trip = Trip.query.get_or_404(trip_id)
    stops = Stop.query.filter_by(trip_id=trip.id).order_by(Stop.arrival_date).all()
    
    return render_template('share_trip.html', trip=trip, stops=stops)
@auth.route('/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    # Ensure the user actually owns this trip before deleting it!
    if trip.user_id == current_user.id:
        db.session.delete(trip)
        db.session.commit()
        flash('Trip deleted successfully.', 'info')
        
    return redirect(url_for('auth.dashboard'))

@auth.route('/stop/<int:stop_id>/delete', methods=['POST'])
@login_required
def delete_stop(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    trip_id = stop.trip_id
    
    # Security check: Ensure the user owns the trip
    if stop.trip.user_id == current_user.id:
        db.session.delete(stop)
        db.session.commit()
        flash(f'{stop.city_name} removed from itinerary.', 'info')
        
    return redirect(url_for('auth.trip_view', trip_id=trip_id))


@auth.route('/activity/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    trip_id = activity.stop.trip_id
    
    # Security check: Ensure the user owns the trip this activity belongs to
    if activity.stop.trip.user_id == current_user.id:
        db.session.delete(activity)
        db.session.commit()
        flash(f'"{activity.name}" removed.', 'info')
        
    return redirect(url_for('auth.trip_view', trip_id=trip_id))
@auth.route('/profile')
@login_required
def profile():
    # Calculate some travel statistics for the user
    trips = Trip.query.filter_by(user_id=current_user.id).all()
    total_trips = len(trips)
    
    # Count every single stop across all their trips
    total_cities = sum(len(trip.stops) for trip in trips)
    
    return render_template('profile.html', total_trips=total_trips, total_cities=total_cities)
@auth.route('/trip/<int:trip_id>/export')
@login_required
def export_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    stops = Stop.query.filter_by(trip_id=trip.id).order_by(Stop.arrival_date).all()
    total_cost = sum(
        sum(act.cost for act in stop.activities)
        for stop in stops
    )
    return render_template('export_trip.html', trip=trip, stops=stops, total_cost=total_cost)


@auth.route('/trip/<int:trip_id>/checklist/add', methods=['POST'])
@login_required
def add_checklist_item(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    item_name = request.form.get('item_name')
    if item_name:
        new_item = ChecklistItem(trip_id=trip.id, item_name=item_name)
        db.session.add(new_item)
        db.session.commit()
        flash(f'Added "{item_name}" to packing list.', 'success')
        
    return redirect(url_for('auth.trip_view', trip_id=trip.id))


@auth.route('/checklist/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    if item.trip.user_id == current_user.id:
        item.is_packed = not item.is_packed
        db.session.commit()
    return redirect(url_for('auth.trip_view', trip_id=item.trip_id))


@auth.route('/checklist/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    trip_id = item.trip_id
    if item.trip.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('auth.trip_view', trip_id=trip_id))
@auth.route('/trip/<int:trip_id>/notes/add', methods=['POST'])
@login_required
def add_trip_note(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'General')
    
    if title and content:
        new_note = TripNote(trip_id=trip.id, title=title, content=content, category=category)
        db.session.add(new_note)
        db.session.commit()
        flash('Note saved to locker!', 'success')
        
    return redirect(url_for('auth.trip_view', trip_id=trip.id))


@auth.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_trip_note(note_id):
    note = TripNote.query.get_or_404(note_id)
    trip_id = note.trip_id
    if note.trip.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        flash('Note removed.', 'info')
    return redirect(url_for('auth.trip_view', trip_id=trip_id))
# ---------------------------------------------------------
# FEATURE 1 & 3: Participants & Photo Gallery Routes
# ---------------------------------------------------------
@auth.route('/trip/<int:trip_id>/participant/add', methods=['POST'])
@login_required
def add_participant(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    name = request.form.get('name')
    if name:
        new_p = TripParticipant(trip_id=trip.id, name=name)
        db.session.add(new_p)
        db.session.commit()
        flash(f'Added traveler {name}.', 'success')
    return redirect(url_for('auth.trip_view', trip_id=trip.id))


@auth.route('/participant/<int:p_id>/delete', methods=['POST'])
@login_required
def delete_participant(p_id):
    p = TripParticipant.query.get_or_404(p_id)
    trip_id = p.trip_id
    if p.trip.user_id == current_user.id:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('auth.trip_view', trip_id=trip_id))


@auth.route('/trip/<int:trip_id>/photo/add', methods=['POST'])
@login_required
def add_trip_photo(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    image_url = request.form.get('image_url')
    caption = request.form.get('caption')
    if image_url:
        new_photo = TripPhoto(trip_id=trip.id, image_url=image_url, caption=caption)
        db.session.add(new_photo)
        db.session.commit()
        flash('Memory photo added!', 'success')
    return redirect(url_for('auth.trip_view', trip_id=trip.id))


@auth.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_trip_photo(photo_id):
    photo = TripPhoto.query.get_or_404(photo_id)
    trip_id = photo.trip_id
    if photo.trip.user_id == current_user.id:
        db.session.delete(photo)
        db.session.commit()
    return redirect(url_for('auth.trip_view', trip_id=trip_id))


# ---------------------------------------------------------
# FEATURE 2: AI Smart Recommendations Engine (Mock/Heuristic)
# ---------------------------------------------------------
@auth.route('/stop/<int:stop_id>/ai-recommendations')
@login_required
def ai_recommendations(stop_id):
    stop = Stop.query.get_or_404(stop_id)
    if stop.trip.user_id != current_user.id:
        return redirect(url_for('auth.dashboard'))
    
    city = stop.city_name.strip().title()
    
    # Custom smart recommendations database for local Indian travel hubs
    recommendations = {
        "Ahmedabad": [
            {"title": "Sabarmati Ashram", "type": "Sightseeing", "desc": "Historic center of Mahatma Gandhi's non-violent freedom struggle."},
            {"title": "Manek Chowk Night Street Food", "type": "Food", "desc": "Famous night market known for Pav Bhaji, Chocolate Sandwich, and Ghughra."},
            {"title": "Adalaj Stepwell", "type": "Architecture", "desc": "Magnificent five-story subterranean architectural marvel built in 1499."}
        ],
        "Veraval": [
            {"title": "Bhalka Tirth", "type": "Heritage", "desc": "Sacred holy site where Lord Krishna took his last earthly journey."},
            {"title": "Veraval Fishing Harbor", "type": "Culture", "desc": "One of the largest fishing ports in Western India, vibrant boat docks."},
            {"title": "Somnath Beach Walk", "type": "Nature", "desc": "Scenic coastline walk right beside the Arabian Sea."}
        ],
        "Somnath": [
            {"title": "Somnath Temple Aarti", "type": "Spiritual", "desc": "First among the 12 Jyotirlinga shrines, renowned for light and sound show."},
            {"title": "Prabhas Patan Museum", "type": "History", "desc": "Houses ancient temple fragments, sculptures, and old relics."},
            {"title": "Geeta Mandir", "type": "Temple", "desc": "Features carvings of Shrimad Bhagavad Gita pillars across white marble."}
        ]
    }
    
    # Default fallback generator for any custom city typed by the user
    city_recs = recommendations.get(city, [
        {"title": f"Explore {city} City Center", "type": "Sightseeing", "desc": f"Walk around local markets and discover hidden gems in {city}."},
        {"title": f"Local Cuisine Tasting", "type": "Food", "desc": f"Try signature local delicacies and traditional street food in {city}."},
        {"title": f"{city} Heritage Landmark", "type": "Culture", "desc": f"Visit the primary historical monument or viewpoint in {city}."}
    ])
    
    return render_template('ai_recommendations.html', stop=stop, city_recs=city_recs)