# ALX Travel App - Task 0x01

## API Development for Listings and Bookings in Django

This project extends the previous task (0x00) by implementing **API endpoints** for managing listings and bookings, with full CRUD operations and interactive documentation via **Swagger** and **ReDoc**.

---

## Project Structure

alx_travel_app/
├── listings/
│ ├── models.py # Database models (Listing, Booking, Review)
│ ├── serializers.py # API serializers (Listing, Booking)
│ ├── views.py # API ViewSets for Listing and Booking
│ ├── urls.py # Router-based API URL configuration
│ └── management/
│ └── commands/
│ └── seed.py # Database seeding command
├── alxtravelapp/
│ ├── urls.py # Project root URL configuration (includes Swagger & app URLs)
├── README.md
└── ...


---

## Implemented Features

### 1. Listings API
- **Endpoints**:  
  - `GET /api/listings/` – List all listings  
  - `POST /api/listings/` – Create a new listing  
  - `GET /api/listings/{id}/` – Retrieve a specific listing  
  - `PUT/PATCH /api/listings/{id}/` – Update a listing  
  - `DELETE /api/listings/{id}/` – Delete a listing  

### 2. Bookings API
- **Endpoints**:  
  - `GET /api/bookings/` – List all bookings  
  - `POST /api/bookings/` – Create a new booking  
  - `GET /api/bookings/{id}/` – Retrieve a specific booking  
  - `PUT/PATCH /api/bookings/{id}/` – Update a booking  
  - `DELETE /api/bookings/{id}/` – Delete a booking  

### 3. Swagger & ReDoc Documentation
- **Swagger UI**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)  
- **ReDoc**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)  

Interactive documentation allows you to explore and test endpoints directly in the browser.

---

## Serializers

### ListingSerializer
- Validates `price_per_night > 0`
- Read-only: `listing_id`, `created_at`, `updated_at`

### BookingSerializer
- Validates `end_date > start_date`
- Validates `total_price > 0`
- Read-only: `booking_id`, `created_at`

---

## Database Seeding

You can still seed the database with **users, listings, bookings, and reviews** for testing:

```bash
# Basic seeding
python manage.py seed

# Custom quantities
python manage.py seed --users 50 --listings 30 --bookings 100 --reviews 80
```

## Installation and Setup

### 1. Clone the repo:

```bash
git clone https://github.com/<your-username>/alx_travel_app_0x01.git
cd alx_travel_app_0x01/alx_travel_app
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start the server:

```bash
python manage.py runserver
```

### 5. Access the API:

- Listings: `http://127.0.0.1:8000/api/listings/`

- Bookings: `http://127.0.0.1:8000/api/bookings/`

- Swagger docs: `http://127.0.0.1:8000/swagger/`

## Key Features

- CRUD APIs for Listings and Bookings

- UUID Primary Keys for scalability

- Validation at both model and serializer level

- Swagger/ReDoc for interactive API documentation

- Database seeding with realistic data using Faker

- Indexed fields for query optimization


- Repository: `alx_travel_app_0x01`
- Directory: `alx_travel_app`
- Author: `Vincent Okoli`