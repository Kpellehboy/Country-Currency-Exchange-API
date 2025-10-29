# 🌍 Country Currency & Exchange API

A RESTful API built with Python and Flask that fetches country and exchange rate data from external sources, computes estimated economic indicators, and provides CRUD operations with local caching in a MySQL database.

## 🚀 Getting Started

This guide will help you set up and run the project locally.

### Prerequisites

You need the following installed on your machine:

  * **Python 3.8+**
  * **pip** (Python package installer)
  * A running **MySQL** instance.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Kpellehboy/Country-Currency-Exchange-API
    cd country-currency-api
    ```

2.  **Create and activate a Python virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: You will need to create a `requirements.txt` file containing all necessary packages, e.g., `Flask`, `Flask-SQLAlchemy`, `requests`, `python-dotenv`, `Pillow`, `matplotlib` or similar for image generation.)*

### Environment Variables

Create a file named **`.env`** in the root directory of the project and add your configuration details. This is crucial for connecting to your MySQL database.

```dotenv
# .env file

# API Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=a_super_secret_key_for_flask_sessions

# Database Configuration (Using Flask-SQLAlchemy format)
# The URL should follow the format: mysql://<user>:<password>@<host>:<port>/<database>
# Replace the placeholders with your actual credentials for the database at
# https://www.phpmyadmin.co/sql.php?server=1&db=sql12804893... (Note: Use your actual DB credentials, not this URL)
MYSQL_USER=your_db_username
MYSQL_PASSWORD=your_db_password
MYSQL_HOST=your_db_host
MYSQL_DB=your_db_name
SQLALCHEMY_DATABASE_URI=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:3306/${MYSQL_DB}

# External API URLs
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_RATE_API_URL=https://open.er-api.com/v6/latest/USD
```

### Database Setup

Your API uses the following structure for the `countries` table. You can use your phpMyAdmin connection to run the necessary SQL to create the table, or use the Flask-SQLAlchemy method (`db.create_all()` in an application context) if implemented in your `app.py`.

**SQL Schema for `countries` table (Example):**

```sql
CREATE TABLE countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    capital VARCHAR(255),
    region VARCHAR(255),
    population BIGINT NOT NULL,
    currency_code VARCHAR(10) NOT NULL,
    exchange_rate DECIMAL(20, 10),
    estimated_gdp DECIMAL(30, 2),
    flag_url VARCHAR(512),
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE metadata (
    key_name VARCHAR(50) PRIMARY KEY,
    value TEXT
);
-- Used to store the last successful refresh timestamp globally
INSERT INTO metadata (key_name, value) VALUES ('last_refreshed_at', NULL) ON DUPLICATE KEY UPDATE value=value;
```

## ▶️ Running the Application

1.  **Ensure your virtual environment is active** and the `.env` file is configured.
2.  **Run the Flask application:**
    ```bash
    flask run
    # The API will typically run on http://127.0.0.1:5000/
    ```
    *(If you use a different entry file or runner, adjust the command.)*

## ⚙️ API Endpoints

The base URL for all endpoints is **`[YOUR_API_BASE_URL]`** (e.g., `http://127.0.0.1:5000`). All responses are in **JSON** format (except `/countries/image` which serves a PNG image).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/countries/refresh` | Fetches, computes, and caches all country and exchange rate data. Recalculates `estimated_gdp`. Generates the summary image. |
| **GET** | `/countries` | Get all cached countries. Supports **filtering** (`?region=...`, `?currency=...`) and **sorting** (`?sort=name_asc`, `?sort=gdp_desc`). |
| **GET** | `/countries/<name>` | Get a single country by its **exact name**. |
| **DELETE** | `/countries/<name>` | Delete a single country record by its **exact name**. |
| **GET** | `/status` | Shows the total number of countries cached and the timestamp of the last successful refresh. |
| **GET** | `/countries/image` | Serves the generated summary image (`cache/summary.png`). Returns 404/JSON error if the image is not found. |

### Example Queries

  * **Filter by Region and Sort by GDP (Descending):**
    ```
    GET /countries?region=Africa&sort=gdp_desc
    ```
  * **Filter by Currency Code:**
    ```
    GET /countries?currency=NGN
    ```
  * **Get Status:**
    ```
    GET /status
    ```

## ⚠️ Validation and Error Handling

All error responses are returned as consistent JSON objects:

| Status Code | Error Response Example | Notes |
| :--- | :--- | :--- |
| **400 Bad Request** | `{"error": "Validation failed", "details": {"population": "is required"}}` | For invalid or missing required data in a PUT/POST operation, or invalid query parameters. |
| **404 Not Found** | `{"error": "Country not found"}` | When a country name does not match any record for GET/DELETE operations. |
| **500 Internal Server Error** | `{"error": "Internal server error"}` | General server-side exceptions. |
| **503 Service Unavailable** | `{"error": "External data source unavailable", "details": "Could not fetch data from restcountries.com"}` | If external APIs (Countries or Exchange Rate) fail or timeout during `/countries/refresh`. |

## 🎨 Image Generation (`/countries/image`)

On every successful run of **`POST /countries/refresh`**, a summary image is generated and saved to a **`cache/summary.png`** file.

**Image Content:**

1.  Total number of countries cached.
2.  Top 5 countries by estimated GDP.
3.  Timestamp of the last refresh.

The `/countries/image` endpoint serves this file directly.

## 🛠️ Implementation Notes

  * **Database:** **MySQL** is used via **Flask-SQLAlchemy** (or similar wrapper for Python/Flask).
  * **Caching:** Data is only fetched and updated in the database upon a **`POST /countries/refresh`** request.
  * **GDP Calculation:** `estimated_gdp = population × random(1000–2000) ÷ exchange_rate`. The random multiplier is generated *fresh* for each country on every refresh.
  * **Country Matching:** Existing records are matched by **`name`** (case-insensitive) for update/insert logic.
  * **Currency Handling:**
      * If multiple currencies exist, only the **first** one is used.
      * If no currencies exist, `currency_code`, `exchange_rate` are set to `null`, and `estimated_gdp` is set to `0`.
      * If the currency code is not found in the exchange rate data (USD base), `exchange_rate` and `estimated_gdp` are set to `null`.
  * **File Structure:**
    ```
    .
    ├── .env
    ├── app.py          # Main Flask application and routes
    ├── requirements.txt
    ├── models.py       # (Optional) Database models
    ├── refresh_logic.py # (Optional) Logic for POST /countries/refresh
    ├── cache/
    │   └── summary.png # The generated image file
    └── ...
    ```

## 📦 Dependencies

The core dependencies for this project are:

  * `Flask`
  * `Flask-SQLAlchemy` (or `Flask-MySQL` and `PyMySQL`)
  * `requests` (for external API calls)
  * `python-dotenv` (for environment variable loading)
  * `Pillow` (PIL) and/or `matplotlib` (for simple image generation)
  * `pandas` (optional, for sorting and filtering if not done via SQL)

*(Ensure these are listed correctly in your `requirements.txt`.)*

## 🧪 Testing & Deployment URL

The API was tested using **Postman** to confirm all endpoints, filters, sorting, and error handling meet the requirements.
Deployed on Railway: https://backendwizardsstage0-production.up.railway.app/
