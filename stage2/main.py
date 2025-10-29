from flask import Flask, jsonify, request, send_file
from db import get_db_connection
from models import create_table
from utils import fetch_countries, fetch_exchange_rates, compute_estimated_gdp, generate_summary_image
import datetime
import os

app = Flask(__name__)

create_table()

# GET /Test endpoint
@app.route("/", methods=["GET"])
def test_endpoint():
        return jsonify({"message": "Endpoint is working"}), 200

# countries router
@app.route("/countries/refresh", methods=["POST"])
def refresh_countries():
    try:
        countries = fetch_countries()
        rates = fetch_exchange_rates()
    except Exception as e:
        return jsonify({"error": "External data source unavailable", "details": str(e)}), 503

    conn = get_db_connection()
    cursor = conn.cursor()

    for c in countries:
        name = c.get("name")
        capital = c.get("capital")
        region = c.get("region")
        population = c.get("population", 0)
        flag = c.get("flag")

        # Currency handling logic
        currencies = c.get("currencies", [])
        if currencies:
            # Store only the first currency code from the array
            currency_code = currencies[0]["code"]
            # Check if currency_code exists in exchange rates API
            exchange_rate = rates.get(currency_code) if currency_code in rates else None
        else:
            # If currencies array is empty
            currency_code = None
            exchange_rate = None
        
        # Calculate estimated_gdp based on currency/exchange rate availability
        if not currencies:
            # Empty currencies array: set estimated_gdp to 0
            estimated_gdp = 0
        elif currency_code not in rates:
            # Currency not found in exchange rates API: set estimated_gdp to null
            estimated_gdp = None
        else:
            # Normal case: calculate with fresh random multiplier
            estimated_gdp = compute_estimated_gdp(population, exchange_rate)

        # Check if country exists (case-insensitive match)
        cursor.execute("SELECT id FROM countries WHERE LOWER(name) = LOWER(%s)", (name,))
        existing_country = cursor.fetchone()

        if existing_country:
            # Update existing country
            cursor.execute("""
            UPDATE countries SET 
                capital=%s,
                region=%s,
                population=%s,
                currency_code=%s,
                exchange_rate=%s,
                estimated_gdp=%s,
                flag_url=%s,
                last_refreshed_at=CURRENT_TIMESTAMP
            WHERE LOWER(name) = LOWER(%s)
            """, (capital, region, population, currency_code, exchange_rate, estimated_gdp, flag, name))
        else:
            # Insert new country
            cursor.execute("""
            INSERT INTO countries (name, capital, region, population, currency_code, exchange_rate, estimated_gdp, flag_url, last_refreshed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)
            """, (name, capital, region, population, currency_code, exchange_rate, estimated_gdp, flag))

    conn.commit()

    # Generate summary image
    cursor.execute("SELECT name, estimated_gdp FROM countries ORDER BY estimated_gdp DESC LIMIT 5")
    top5 = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM countries")
    total = cursor.fetchone()[0]

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    generate_summary_image(top5, total, timestamp)

    conn.close()
    return jsonify({"message": "Countries refreshed successfully", "total": total}), 200

# GET /countries
@app.route("/countries", methods=["GET"])
def get_countries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM countries"
    filters = []
    values = []

    if "region" in request.args:
        filters.append("region=%s")
        values.append(request.args["region"])
    if "currency" in request.args:
        filters.append("currency_code=%s")
        values.append(request.args["currency"])

    if filters:
        query += " WHERE " + " AND ".join(filters)

    if "sort" in request.args:
        if request.args["sort"] == "gdp_desc":
            query += " ORDER BY estimated_gdp DESC"

    cursor.execute(query, values)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# GET /countries/<name>
@app.route("/countries/<string:name>", methods=["GET"])
def get_country(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM countries WHERE LOWER(name)=LOWER(%s)", (name,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return jsonify({"error": "Country not found"}), 404
    return jsonify(result)

# DELETE /countries/<name>
@app.route("/countries/<string:name>", methods=["DELETE"])
def delete_country(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM countries WHERE LOWER(name)=LOWER(%s)", (name,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Country not found"}), 404
    conn.close()
    return jsonify({"message": f"{name} deleted successfully"})

# GET /status
@app.route("/status", methods=["GET"])
def get_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MAX(last_refreshed_at) FROM countries")
    count, last_refreshed = cursor.fetchone()
    conn.close()
    return jsonify({
        "total_countries": count,
        "last_refreshed_at": last_refreshed.strftime("%Y-%m-%d %H:%M:%S") if last_refreshed else None
    })
#
# GET /countries/image
@app.route("/countries/image", methods=["GET"])
def get_image():
    try:
        if os.path.exists("cache_summary.png"):
            return send_file("cache_summary.png", mimetype="image/png")
        else:
            return jsonify({"error": "Summary image not found"}), 404
    except Exception as e:
        return jsonify({"error": "Summary image not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)