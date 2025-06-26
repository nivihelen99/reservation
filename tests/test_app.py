import unittest
import json
from datetime import datetime, timedelta, timezone
import pytz # Import pytz
from app import app, db, Reservation, PST, MAX_RESERVATION_DURATION, MIN_RESERVATION_DURATION, ADVANCE_BOOKING_LIMIT

class ReservationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for tests
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def _make_reservation(self, username, start_delta_days, start_hour, duration_minutes):
        """Helper to create datetime objects for reservations."""
        now_pst = datetime.now(PST)
        start_time = (now_pst + timedelta(days=start_delta_days)).replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=duration_minutes)
        return {
            "username": username,
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'), # Naive string, as client would send
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S')    # Naive string
        }

    def test_01_create_reservation_success(self):
        """Test successful reservation creation."""
        payload = self._make_reservation("testuser", 1, 14, 60) # Tomorrow, 2 PM, 1 hour
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], "testuser")
        with app.app_context(): # Add app context for DB query
            self.assertTrue(Reservation.query.count() == 1)

    def test_02_get_reservations_empty(self):
        """Test getting reservations when none exist."""
        response = self.client.get('/reservations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_03_get_reservations_with_data(self):
        """Test getting reservations when some exist."""
        payload = self._make_reservation("testuser1", 1, 10, 60)
        self.client.post('/reservations', json=payload)

        payload2 = self._make_reservation("testuser2", 2, 11, 120)
        self.client.post('/reservations', json=payload2)

        response = self.client.get('/reservations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['username'], "testuser1")
        self.assertEqual(data[1]['username'], "testuser2")

    def test_04_create_reservation_conflict(self):
        """Test creating a reservation that conflicts with an existing one."""
        payload1 = self._make_reservation("user_A", 1, 15, 60) # Day+1, 3 PM - 4 PM
        self.client.post('/reservations', json=payload1)

        # Attempt to book overlapping slot
        payload2 = self._make_reservation("user_B", 1, 15, 30) # Day+1, 3 PM - 3:30 PM (Conflict)
        response = self.client.post('/reservations', json=payload2)
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn("overlaps with an existing reservation", data['error'])

        # Attempt to book slot that starts during existing one
        payload3 = self._make_reservation("user_C", 1, 15, 90) # Day+1, 3:30 PM - 5 PM (Conflict with user_A's 3-4pm)
        adjusted_payload3 = self._make_reservation("user_C", 1, 15, 30) # Day+1, 3:00 PM
        adjusted_payload3['start_time'] = (datetime.strptime(payload1['start_time'], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        adjusted_payload3['end_time'] = (datetime.strptime(adjusted_payload3['start_time'], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S')

        response = self.client.post('/reservations', json=adjusted_payload3)
        self.assertEqual(response.status_code, 409)


    def test_05_create_reservation_past_date(self):
        """Test creating a reservation in the past."""
        payload = self._make_reservation("pastuser", -1, 10, 60) # Yesterday, 10 AM
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Reservations can only be made for future dates/times", data['error'])

    def test_06_create_reservation_end_before_start(self):
        """Test creating a reservation where end time is before start time."""
        payload = self._make_reservation("chronouser", 1, 14, -30) # Duration -30 mins
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("End time must be after start time", data['error'])

    def test_07_create_reservation_min_duration(self):
        """Test minimum reservation duration."""
        # Valid: Exactly MIN_RESERVATION_DURATION
        min_duration_minutes = MIN_RESERVATION_DURATION.total_seconds() / 60
        payload_valid = self._make_reservation("minuser_ok", 1, 10, int(min_duration_minutes))
        response_valid = self.client.post('/reservations', json=payload_valid)
        self.assertEqual(response_valid.status_code, 201, f"Response data: {response_valid.data.decode()}")


        # Invalid: Shorter than MIN_RESERVATION_DURATION
        payload_invalid = self._make_reservation("minuser_bad", 1, 11, int(min_duration_minutes - 1))
        response_invalid = self.client.post('/reservations', json=payload_invalid)
        self.assertEqual(response_invalid.status_code, 400)
        data = json.loads(response_invalid.data)
        self.assertIn("Minimum reservation duration", data['error'])


    def test_08_create_reservation_max_duration(self):
        """Test maximum reservation duration."""
        max_duration_minutes = MAX_RESERVATION_DURATION.total_seconds() / 60
        # Valid: Exactly MAX_RESERVATION_DURATION
        payload_valid = self._make_reservation("maxuser_ok", 1, 12, int(max_duration_minutes))
        response_valid = self.client.post('/reservations', json=payload_valid)
        self.assertEqual(response_valid.status_code, 201, f"Response data: {response_valid.data.decode()}")

        # Invalid: Longer than MAX_RESERVATION_DURATION
        payload_invalid = self._make_reservation("maxuser_bad", 1, 13, int(max_duration_minutes + 1))
        response_invalid = self.client.post('/reservations', json=payload_invalid)
        self.assertEqual(response_invalid.status_code, 400)
        data = json.loads(response_invalid.data)
        self.assertIn("Maximum reservation duration", data['error'])

    def test_09_create_reservation_too_far_in_advance(self):
        """Test reservation too far in advance."""
        days_too_far = ADVANCE_BOOKING_LIMIT.days + 1
        payload = self._make_reservation("futurelooker", days_too_far, 10, 60)
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("days in advance", data['error'])

    def test_10_create_reservation_boundary_advance_limit(self):
        """Test reservation at the exact advance booking limit."""
        # On the last allowed day
        days_at_limit = ADVANCE_BOOKING_LIMIT.days

        # Calculate start_time for the boundary condition
        now_pst = datetime.now(PST)
        # Start of today PST
        start_of_today_pst = now_pst.replace(hour=0, minute=0, second=0, microsecond=0)
        # Last allowed day, e.g., 10 AM on that day
        boundary_start_time = start_of_today_pst + timedelta(days=days_at_limit) + timedelta(hours=10)

        payload = {
            "username": "boundaryuser",
            "start_time": boundary_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (boundary_start_time + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 201, f"Failed for boundary condition. Response: {response.data.decode()}")


    def test_11_get_reservations_filter_day(self):
        """Test filtering reservations by day."""
        now_pst = datetime.now(PST)

        # Reservation for today
        start_today = (now_pst + timedelta(hours=1 if now_pst.hour < 22 else 0)).replace(minute=0, second=0, microsecond=0) # ensure it's in future
        if start_today <= now_pst : # if it's too late in the day, schedule for tomorrow and adjust test logic if needed
             start_today = (now_pst + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

        payload_today = {
            "username": "todayuser",
            "start_time": start_today.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (start_today + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.client.post('/reservations', json=payload_today)

        # Reservation for tomorrow
        start_tomorrow = (now_pst + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        payload_tomorrow = {
            "username": "tomorrowuser",
            "start_time": start_tomorrow.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (start_tomorrow + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.client.post('/reservations', json=payload_tomorrow)

        # Check if the "today" reservation is actually for today PST
        # This test might be flaky if run exactly at midnight or if day calculation is off
        # The backend uses `now_pst.replace(hour=0, minute=0, second=0, microsecond=0)` for "today_start"
        # So we need to ensure `start_today` falls within that range.

        # If start_today was pushed to tomorrow due to timing:
        is_today_reservation_actually_today = start_today.date() == now_pst.date()

        response = self.client.get('/reservations?view=day')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        if is_today_reservation_actually_today:
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['username'], "todayuser")
        else:
            # If the "today" reservation was actually made for tomorrow (e.g. script run late at night)
            # then the "day" filter for the *actual current day* should return 0 results.
            self.assertEqual(len(data), 0, "Expected 0 reservations for 'today' if 'todayuser' was scheduled for tomorrow.")


    def test_12_get_reservations_filter_week(self):
        """Test filtering reservations by week."""
        now_pst = datetime.now(PST)
        start_of_current_week_pst = (now_pst - timedelta(days=now_pst.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

        reservations_in_week_details = []

        # Create two reservations guaranteed to be in the current week if possible,
        # or in the next week if current week is almost over and they'd be in the past.

        # Reservation 1: Try for Tuesday 10 AM of current week
        res1_time_target = start_of_current_week_pst + timedelta(days=1, hours=10) # Target: Tuesday 10 AM
        if res1_time_target <= now_pst: # If target is in the past (e.g. it's Wednesday)
            res1_time_target = (now_pst + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0) # Tomorrow 10 AM

        payload1 = {
            "username": "weekuser1",
            "start_time": res1_time_target.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (res1_time_target + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.client.post('/reservations', json=payload1)
        # Check if this reservation falls into the current week view
        if res1_time_target >= start_of_current_week_pst and \
           res1_time_target < (start_of_current_week_pst + timedelta(weeks=1)):
            reservations_in_week_details.append("weekuser1")

        # Reservation 2: Try for Thursday 11 AM of current week
        res2_time_target = start_of_current_week_pst + timedelta(days=3, hours=11) # Target: Thursday 11 AM
        if res2_time_target <= now_pst: # If target is in the past
             # Try for tomorrow 11 AM, if that's still in the same week.
            potential_res2_time = (now_pst + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0)
            if potential_res2_time < (start_of_current_week_pst + timedelta(weeks=1)):
                res2_time_target = potential_res2_time
            else: # Otherwise, this reservation won't be in the current week, so don't create or expect it.
                res2_time_target = None


        if res2_time_target:
            payload2 = {
                "username": "weekuser2",
                "start_time": res2_time_target.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": (res2_time_target + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            }
            self.client.post('/reservations', json=payload2)
            if res2_time_target >= start_of_current_week_pst and \
               res2_time_target < (start_of_current_week_pst + timedelta(weeks=1)):
                reservations_in_week_details.append("weekuser2")

        # Reservation for next week (should not appear in 'week' filter)
        start_next_week_pst = start_of_current_week_pst + timedelta(weeks=1, hours=10)
        payload_next_week = {
            "username": "nextweekuser",
            "start_time": start_next_week_pst.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": (start_next_week_pst + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.client.post('/reservations', json=payload_next_week)

        response = self.client.get('/reservations?view=week')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(len(data), len(reservations_in_week_details))
        usernames_in_response = sorted([r['username'] for r in data])
        self.assertEqual(usernames_in_response, sorted(reservations_in_week_details))
        self.assertNotIn("nextweekuser", usernames_in_response)

    def test_13_missing_fields(self):
        """Test reservation with missing fields."""
        payload = self._make_reservation("testuser", 1, 14, 60)

        for field in ["username", "start_time", "end_time"]:
            bad_payload = payload.copy()
            del bad_payload[field]
            response = self.client.post('/reservations', json=bad_payload)
            self.assertEqual(response.status_code, 400, f"Failed for missing field: {field}")
            data = json.loads(response.data)
            self.assertIn("Missing required fields", data['error'])

    def test_14_invalid_date_format(self):
        """Test reservation with invalid date format."""
        payload = {
            "username": "dateformer",
            "start_time": "July 25, 2025 10:00 AM", # Invalid format
            "end_time": "2025-07-25 11:00:00"
        }
        response = self.client.post('/reservations', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Invalid date format", data['error'])

if __name__ == '__main__':
    unittest.main()
