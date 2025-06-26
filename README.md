# Server Reservation System

A web-based calendar-driven reservation system that allows users to reserve server time in customizable date + time ranges.

## Features

*   Calendar UI for date selection.
*   Time range selection (start and end time).
*   View upcoming and active reservations.
*   Conflict prevention: No overlapping reservations allowed.
*   Configurable reservation rules:
    *   Reservations for future dates only.
    *   Minimum time slot: 15 minutes.
    *   Maximum duration per reservation: 4 hours.
    *   Advance booking limit: Up to 30 days in advance.
*   All times are handled in PST (America/Los_Angeles).

## Technical Stack

*   **Backend:** Python + Flask, Flask-SQLAlchemy
*   **Frontend:** HTML, JavaScript, Bootstrap
*   **Calendar UI:** Flatpickr
*   **Database:** SQLite
*   **Template Engine:** Jinja2

## Project Structure

```
.
├── app.py                # Main Flask application, API logic, database models
├── reservations.db       # SQLite database file (created on first run)
├── templates/
│   └── index.html        # Main HTML page for the UI
├── tests/
│   └── test_app.py       # Backend unit tests
├── static/               # (Optional: for CSS, JS, images if not using CDNs)
├── README.md             # This file
└── requirements.txt      # Python dependencies (to be generated)
```

## Setup and Installation

1.  **Clone the repository (if applicable) or download the files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file with the following content:
    ```
    Flask
    Flask-SQLAlchemy
    python-dateutil
    pytz
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    The database (`reservations.db`) and its tables will be created automatically when you first run the Flask application.

## Running the Application

1.  **Ensure your virtual environment is activated.**

2.  **Run the Flask development server:**
    ```bash
    python app.py
    ```

3.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Running Tests

1.  **Ensure your virtual environment is activated and dependencies are installed.**

2.  **Navigate to the project's root directory and run:**
    ```bash
    python -m unittest discover tests
    ```

## API Endpoints

All API endpoints are prefixed by the application's base URL (e.g., `http://127.0.0.1:5000`).

### 1. Create a Reservation

*   **Endpoint:** `POST /reservations`
*   **Description:** Creates a new reservation.
*   **Request Body (JSON):**
    ```json
    {
        "username": "string (required)",
        "start_time": "string (required, ISO-like format: 'YYYY-MM-DD HH:MM', PST assumed)",
        "end_time": "string (required, ISO-like format: 'YYYY-MM-DD HH:MM', PST assumed)"
    }
    ```
*   **Responses:**
    *   `201 Created`: Reservation successful. Returns the created reservation object.
        ```json
        {
            "id": 1,
            "username": "testuser",
            "start_time": "2025-07-02T14:00:00-07:00", // Example ISO format with offset
            "end_time": "2025-07-02T15:00:00-07:00"
        }
        ```
    *   `400 Bad Request`: Invalid input, missing fields, invalid date format, or rule violation (e.g., end time before start, duration limits, past date, too far in advance). Includes an error message.
        ```json
        { "error": "Descriptive error message" }
        ```
    *   `409 Conflict`: Requested time slot overlaps with an existing reservation.
        ```json
        { "error": "Requested time slot is already reserved..." }
        ```

### 2. Get Reservations

*   **Endpoint:** `GET /reservations`
*   **Description:** Retrieves a list of upcoming/active reservations.
*   **Query Parameters:**
    *   `view` (optional): Filters the reservations.
        *   `all` (default): Returns all upcoming and active reservations.
        *   `day`: Returns reservations starting on the current day (PST).
        *   `week`: Returns reservations starting within the current week (Monday to Sunday, PST).
*   **Responses:**
    *   `200 OK`: Returns a list of reservation objects. The list can be empty.
        ```json
        [
            {
                "id": 1,
                "username": "testuser",
                "start_time": "2025-07-02T14:00:00-07:00",
                "end_time": "2025-07-02T15:00:00-07:00"
            },
            {
                "id": 2,
                "username": "anotheruser",
                "start_time": "2025-07-03T10:00:00-07:00",
                "end_time": "2025-07-03T12:00:00-07:00"
            }
        ]
        ```

## Configuration

The following parameters are defined in `app.py` and can be adjusted:

*   `SQLALCHEMY_DATABASE_URI`: Currently `sqlite:///reservations.db`. Can be changed to use PostgreSQL or other databases supported by SQLAlchemy.
*   `MAX_RESERVATION_DURATION`: Currently `timedelta(hours=4)`.
*   `MIN_RESERVATION_DURATION`: Currently `timedelta(minutes=15)`.
*   `ADVANCE_BOOKING_LIMIT`: Currently `timedelta(days=30)`.
*   `PST`: Timezone, currently `pytz.timezone('America/Los_Angeles')`.

## Deployment (Conceptual for Production)

For a production environment, the Flask development server is not suitable. Consider the following setup:

*   **WSGI Server:** Gunicorn or uWSGI to run the Flask application.
*   **Web Server/Reverse Proxy:** Nginx or Apache to serve static files, handle HTTPS, and proxy requests to the WSGI server.
*   **Database:** A more robust database like PostgreSQL is recommended for production.
*   **Process Management:** Systemd or Supervisor to manage the Gunicorn/uWSGI process.

**Example Gunicorn command:**
```bash
gunicorn --workers 3 --bind unix:yourapp.sock -m 007 app:app
```
Nginx would then be configured to proxy pass to `yourapp.sock`.

## Future Enhancements (Not in MVP)

*   User login & authentication
*   Email notifications on reservation
*   Admin panel to approve/delete reservations
*   Support recurring reservations
*   Full REST API endpoints for integration (e.g., update, delete reservations)
