from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz
from dateutil import parser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the PST timezone
PST = pytz.timezone('America/Los_Angeles')

# Maximum reservation duration (e.g., 4 hours)
MAX_RESERVATION_DURATION = timedelta(hours=4)
# Minimum time slot (15 minutes)
MIN_RESERVATION_DURATION = timedelta(minutes=15)
# Advance booking limit (30 days)
ADVANCE_BOOKING_LIMIT = timedelta(days=30)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.username} from {self.start_time} to {self.end_time}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not all([username, start_time_str, end_time_str]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Parse and localize to PST. Assume input is naive and represents PST.
        start_time = PST.localize(parser.isoparse(start_time_str))
        end_time = PST.localize(parser.isoparse(end_time_str))
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO format YYYY-MM-DD HH:MM"}), 400

    now_pst = datetime.now(PST)

    # Validate: Start time must be in the future
    if start_time <= now_pst:
        return jsonify({"error": "Reservations can only be made for future dates/times"}), 400

    # Validate: End time must be after start time
    if end_time <= start_time:
        return jsonify({"error": "End time must be after start time"}), 400

    # Validate: Minimum reservation duration
    if (end_time - start_time) < MIN_RESERVATION_DURATION:
        return jsonify({"error": f"Minimum reservation duration is {MIN_RESERVATION_DURATION.total_seconds() / 60} minutes"}), 400

    # Validate: Maximum reservation duration
    if (end_time - start_time) > MAX_RESERVATION_DURATION:
        return jsonify({"error": f"Maximum reservation duration is {MAX_RESERVATION_DURATION.total_seconds() / 3600} hours"}), 400

    # Validate: Advance booking limit
    if start_time > (now_pst + ADVANCE_BOOKING_LIMIT):
        return jsonify({"error": f"Reservations can only be made up to {ADVANCE_BOOKING_LIMIT.days} days in advance"}), 400

    # Validate: No overlapping reservations
    overlapping_reservations = Reservation.query.filter(
        (Reservation.start_time < end_time) & (Reservation.end_time > start_time)
    ).all()

    if overlapping_reservations:
        return jsonify({"error": "Requested time slot is already reserved or overlaps with an existing reservation"}), 409

    new_reservation = Reservation(username=username, start_time=start_time, end_time=end_time)
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify(new_reservation.to_dict()), 201

@app.route('/reservations', methods=['GET'])
def get_reservations():
    view = request.args.get('view', 'all') # 'all', 'day', 'week'
    now_pst = datetime.now(PST)

    query = Reservation.query.filter(Reservation.end_time > now_pst) # Only future/active

    if view == 'day':
        today_start = now_pst.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        query = query.filter(Reservation.start_time >= today_start, Reservation.start_time < today_end)
    elif view == 'week':
        # Start of the current week (assuming Monday is the first day)
        week_start = (now_pst - timedelta(days=now_pst.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(weeks=1)
        query = query.filter(Reservation.start_time >= week_start, Reservation.start_time < week_end)

    reservations = query.order_by(Reservation.start_time).all()
    return jsonify([r.to_dict() for r in reservations]), 200

from flask import Flask, request, jsonify, render_template # Added render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pytz
from dateutil import parser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the PST timezone
PST = pytz.timezone('America/Los_Angeles')

# Maximum reservation duration (e.g., 4 hours)
MAX_RESERVATION_DURATION = timedelta(hours=4)
# Minimum time slot (15 minutes)
MIN_RESERVATION_DURATION = timedelta(minutes=15)
# Advance booking limit (30 days)
ADVANCE_BOOKING_LIMIT = timedelta(days=30)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.username} from {self.start_time} to {self.end_time}>'

    def to_dict(self):
        # Ensure times are converted to PST for consistent ISO format output if they are timezone-aware
        # If stored as naive in DB but representing PST, localize before formatting
        # If stored as UTC, convert to PST then format

        # Assuming start_time and end_time from DB are already correct (e.g. stored as UTC or naive PST)
        # For this example, the backend logic localizes to PST upon creation.
        # So, they should be PST-aware datetime objects.

        # No, the model stores naive datetimes after they've been converted from strings.
        # The API converts them to ISO strings directly.
        # The critical part is that the backend *interprets* incoming naive strings as PST.
        # And stores timezone-aware datetimes in the DB if the DB & SQLAlchemy support it,
        # or converts to UTC then stores naive, or stores naive PST.
        # Given current code, they are stored as timezone-aware after PST.localize().

        return {
            'id': self.id,
            'username': self.username,
            'start_time': self.start_time.isoformat(), # Will include +00:00 if UTC, or -07:00/-08:00 if PST
            'end_time': self.end_time.isoformat()
        }

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    username = data.get('username')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not all([username, start_time_str, end_time_str]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Parse naive date/time string. Backend assumes it's in PST.
        # Then localize it to make it timezone-aware.
        naive_start_time = parser.isoparse(start_time_str)
        naive_end_time = parser.isoparse(end_time_str)

        start_time = PST.localize(naive_start_time)
        end_time = PST.localize(naive_end_time)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM"}), 400

    now_pst = datetime.now(PST)

    # Validate: Start time must be in the future
    if start_time <= now_pst:
        return jsonify({"error": "Reservations can only be made for future dates/times"}), 400

    # Validate: End time must be after start time
    if end_time <= start_time:
        return jsonify({"error": "End time must be after start time"}), 400

    # Validate: Minimum reservation duration
    if (end_time - start_time) < MIN_RESERVATION_DURATION:
        return jsonify({"error": f"Minimum reservation duration is {MIN_RESERVATION_DURATION.total_seconds() / 60} minutes"}), 400

    # Validate: Maximum reservation duration
    if (end_time - start_time) > MAX_RESERVATION_DURATION:
        return jsonify({"error": f"Maximum reservation duration is {MAX_RESERVATION_DURATION.total_seconds() / 3600} hours"}), 400

    # Validate: Advance booking limit
    # Reservations can be made up to ADVANCE_BOOKING_LIMIT days in the future.
    # This means if today is Day 0, the latest reservable day is Day 30.
    # The start_time must be before the beginning of Day 31.
    limit_cutoff_datetime = (now_pst.replace(hour=0, minute=0, second=0, microsecond=0) +
                             ADVANCE_BOOKING_LIMIT +
                             timedelta(days=1))

    if start_time >= limit_cutoff_datetime:
        # To display a user-friendly "last allowed day"
        last_allowed_day = limit_cutoff_datetime - timedelta(days=1)
        return jsonify({
            "error": f"Reservations can only be made up to {ADVANCE_BOOKING_LIMIT.days} days in advance (last available day is {last_allowed_day.strftime('%Y-%m-%d')})"
        }), 400

    # Validate: No overlapping reservations
    # Query needs to handle timezone-aware datetime objects correctly.
    # SQLAlchemy typically converts aware datetimes to UTC for storage in SQLite if not configured otherwise,
    # or stores them as is if the column type supports it (which DateTime does by default with SQLite).
    # Let's assume they are stored as timezone-aware (or converted to a consistent TZ like UTC).
    # For filtering, ensure comparison values are also timezone-aware.
    overlapping_reservations = Reservation.query.filter(
        (Reservation.start_time < end_time) & (Reservation.end_time > start_time)
    ).all()

    if overlapping_reservations:
        return jsonify({"error": "Requested time slot is already reserved or overlaps with an existing reservation"}), 409

    new_reservation = Reservation(username=username, start_time=start_time, end_time=end_time)
    db.session.add(new_reservation)
    db.session.commit()

    return jsonify(new_reservation.to_dict()), 201

@app.route('/reservations', methods=['GET'])
def get_reservations():
    view = request.args.get('view', 'all') # 'all', 'day', 'week'
    now_pst = datetime.now(PST)

    # Base query: only future/active reservations, ordered by start time
    query = Reservation.query.filter(Reservation.end_time > now_pst)

    if view == 'day':
        # Today in PST
        today_start_pst = now_pst.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end_pst = today_start_pst + timedelta(days=1)
        query = query.filter(Reservation.start_time >= today_start_pst, Reservation.start_time < today_end_pst)
    elif view == 'week':
        # Current week in PST, starting Monday
        start_of_week_pst = (now_pst - timedelta(days=now_pst.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week_pst = start_of_week_pst + timedelta(weeks=1)
        query = query.filter(Reservation.start_time >= start_of_week_pst, Reservation.start_time < end_of_week_pst)

    reservations = query.order_by(Reservation.start_time).all()
    return jsonify([r.to_dict() for r in reservations]), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
<<<<<<< feat/calendar-reservation-system
    app.run(host='0.0.0.0', debug=True)
=======
    app.run(debug=True)
>>>>>>> main
