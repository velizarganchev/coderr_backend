# Coderr Backend

The Coderr Backend is a robust REST API built with Django and the Django REST Framework (DRF). It provides functionalities such as user authentication, password reset, profile management, and review systems for business users.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication:**
  - Login and registration with JWT-based authentication.
  - Password reset via email with secure token validation.
- **Profile Management:**
  - Update and manage user profiles.
- **Review System:**
  - Business users can receive and manage reviews.
- **Offers:**
  - Create, update, and delete offers.
  - Retrieve details of specific offers.
- **Orders:**
  - Create, update, and delete orders.
  - Retrieve details of specific orders.
  - Track order status and counts.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/velizarganchev/coderr_backend.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd coderr_backend
   ```

3. **Create and activate a virtual environment:**
   
   ```bash
   python -m venv env
   source env/bin/activate  # On Unix/Mac
   env\Scripts\activate     # On Windows
   ```

4. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

## Usage

1. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

2. **Access the application:**
   
   Open your web browser and navigate to http://127.0.0.1:8000/.

## API Endpoints

- **Authentication**
  - `POST /api/registration/`: Register a new user.
  - `POST /api/login/`: Login a user and return a JWT token.
  - `POST /api/logout/`: Logout a user.
  - `POST /api/auth/password-reset/`: Request a password reset.
  - `POST /api/auth/password-reset-confirm/`: Confirm password reset with token.

- **Profile**
  - `GET /api/profile/`: Retrieve the authenticated user's profile.
  - `GET /api/profile/{id}/`: Retrieve a specific user's profile.
  - `GET /api/profiles/{type}/`: Retrieve profiles by type.
  - `PATCH /api/profile/`: Update the authenticated user's profile.

- **Reviews**
  - `GET /api/reviews/`: List all reviews for the authenticated user.
  - `POST /api/reviews/`: Create a new review.
  - `PATCH /api/reviews/{id}/`: Update a review.
  - `DELETE /api/reviews/{id}/`: Delete a review.

- **Orders**
  - `GET /api/orders/`: List all orders for the authenticated user.
  - `POST /api/orders/`: Create a new order.
  - `GET /api/orders/{id}/`: Retrieve a specific order.
  - `PATCH /api/orders/{id}/`: Update a specific order.
  - `DELETE /api/orders/{id}/`: Delete a specific order.
  - `GET /api/order-count/{id}/`: Retrieve the count of not completed orders for a specific user.
  - `GET /api/completed-order-count/{id}/`: Retrieve the count of completed orders for a specific user.

- **Offers**
  - `GET /api/offers/`: List all offers.
  - `POST /api/offers/`: Create a new offer.
  - `GET /api/offers/{id}/`: Retrieve a specific offer.
  - `PATCH /api/offers/{id}/`: Update a specific offer.
  - `DELETE /api/offers/{id}/`: Delete a specific offer.
  - `GET /api/offerdetails/{id}/`: Retrieve details of a specific offer.

- **Base Info**
  - `GET /api/base-info/`: Retrieve base information including offer count, review count, average rating, and business profile count.

## Testing

1. **Run the tests:**

   ```bash
   python manage.py test
   ```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License.

