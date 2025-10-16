
# Backend Wizards Stage 0 - Dynamic Profile Endpoint

This project implements a simple RESTful API endpoint that returns a user profile along with a dynamic cat fact fetched from the Cat Facts API. The API is designed to demonstrate fetching data from an external API, formatting JSON responses, and returning dynamic content.

## Endpoint

**GET** `/me`

### Response Format

```json
{
  "status": "success",
  "user": {
    "email": "elijahmflomo@gmail.com",
    "name": "Elijah M. Flomo",
    "stack": "Python/Flask"
  },
  "timestamp": "2025-10-16T19:45:00.123Z",
  "fact": "A random cat fact from Cat Facts API"
}
````

## Features

* Returns user profile information (email, full name, backend stack)
* Returns **dynamic timestamp** in UTC ISO 8601 format
* Fetches a **random cat fact** from [Cat Facts API](https://catfact.ninja/fact)
* Handles external API errors gracefully with fallback messages
* Response Content-Type is `application/json`

## Setup Instructions (Local)

### 1. Clone the repository

```bash
git clone https://github.com/Kpellehboy/backend_wizards_stage0.git
cd backend_wizards_stage0
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root with the following content:

```
USER_EMAIL=your.elijahmflomo@gmail.com
USER_NAME=Elijah M. Flomo
USER_STACK=Python/Flask
PORT=5000
```

### 4. Run the server

```bash
python app.py
```

The API will be available at `http://localhost:5000/me`

## Deployment

Deployed on Railway:

`https://backendwizardsstage0-production.up.railway.app/me`

## Testing the Endpoint

* Open a browser, Postman, or curl:

```bash
curl https://backendwizardsstage0-production.up.railway.app/me
```

* Verify:

  * HTTP status: **200 OK**
  * JSON matches the required structure
  * `timestamp` updates dynamically
  * `fact` is fetched freshly each request

## Notes

* This project uses **Python 3.8+**, **Flask**, and **requests** as the backend stack.
* Cat facts are fetched live from the Cat Facts API on each request.
* If the Cat Facts API fails, a fallback message is returned.
* Ideal for learning API integration, JSON formatting, and deployment basics.

## Dependencies

* [Flask](https://flask.palletsprojects.com/)
* [requests](https://requests.readthedocs.io/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

