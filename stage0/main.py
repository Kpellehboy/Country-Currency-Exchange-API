from flask import Flask, Response
import requests
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/me', methods=['GET'])


def get_profile(): # Fetch user details from environment variables
    response = {
        "status": "success",

        "user": {
            "email": os.getenv("USER_EMAIL", "your.elijahmflomo@gmail.com"),
            "name": os.getenv("USER_NAME", "Elijah M. Flomo"),
            "stack": os.getenv("USER_STACK", "Build a Dynamic Profile Endpoint with Flask")
        },
        
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fact": requests.get("https://catfact.ninja/fact").json().get("fact")
    }
    json_output = json.dumps(response, indent=2)

    return Response(
        json_output,
        mimetype='application/json'
    )
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)