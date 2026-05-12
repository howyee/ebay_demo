from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# ===================================
# EBAY APP CREDENTIALS
# ===================================

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# LONG-LIVED REFRESH TOKEN
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

# ACCESS TOKEN WILL AUTO-GENERATE
ACCESS_TOKEN = None

# ===================================
# GET NEW ACCESS TOKEN
# ===================================

def refresh_access_token():

    global ACCESS_TOKEN

    print("\nRefreshing eBay access token...")

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"

    base64_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64_credentials}"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(
        "https://api.sandbox.ebay.com/identity/v1/oauth2/token",
        headers=headers,
        data=data,
        timeout=20
    )

    print(f"Token Response Status: {response.status_code}")
    print(f"Token Response: {response.text}")

    if response.status_code != 200:
        raise Exception(
            f"Failed to refresh token: {response.text}"
        )

    token_json = response.json()

    ACCESS_TOKEN = token_json["access_token"]

    print("\nAccess token refreshed successfully!")

# ===================================
# GET AUTH HEADERS
# ===================================

def get_headers():

    global ACCESS_TOKEN

    # AUTO GENERATE TOKEN IF EMPTY
    if ACCESS_TOKEN is None:
        refresh_access_token()

    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

# ===================================
# HOME PAGE
# ===================================

@app.route("/")
def home():
    return app.send_static_file("index.html")

# ===================================
# GET LISTINGS
# ===================================

@app.route("/api/listings")
def listings():

    global ACCESS_TOKEN

    try:

        print("\n===================================")
        print("STARTING EBAY API REQUEST")
        print("===================================")

        headers = get_headers()

        print("\nFetching inventory items...")

        inventory_response = requests.get(
            "https://api.sandbox.ebay.com/sell/inventory/v1/inventory_item?limit=10",
            headers=headers,
            timeout=20
        )

        print(f"\nInventory Status: {inventory_response.status_code}")

        # ===================================
        # TOKEN EXPIRED -> AUTO REFRESH
        # ===================================

        if inventory_response.status_code == 401:

            print("\nAccess token expired.")
            print("Refreshing token automatically...")

            refresh_access_token()

            headers = get_headers()

            inventory_response = requests.get(
                "https://api.sandbox.ebay.com/sell/inventory/v1/inventory_item?limit=10",
                headers=headers,
                timeout=20
            )

            print(f"\nRetry Status: {inventory_response.status_code}")

        # ===================================
        # FAIL IF STILL ERROR
        # ===================================

        if inventory_response.status_code != 200:

            print("\nInventory API failed:")
            print(inventory_response.text)

            return jsonify({
                "error": inventory_response.text
            }), 500

        inventory_json = inventory_response.json()

        inventory_items = inventory_json.get(
            "inventoryItems",
            []
        )

        print(f"\nFound {len(inventory_items)} inventory items")

        final_data = []

        # ===================================
        # GET OFFERS
        # ===================================

        for item in inventory_items:

            sku = item.get("sku")

            print(f"\nProcessing SKU: {sku}")

            offer_response = requests.get(
                f"https://api.sandbox.ebay.com/sell/inventory/v1/offer?sku={sku}",
                headers=headers,
                timeout=20
            )

            # TOKEN EXPIRED DURING LOOP
            if offer_response.status_code == 401:

                print("\nOffer token expired.")
                print("Refreshing token automatically...")

                refresh_access_token()

                headers = get_headers()

                offer_response = requests.get(
                    f"https://api.sandbox.ebay.com/sell/inventory/v1/offer?sku={sku}",
                    headers=headers,
                    timeout=20
                )

            offers = []

            if offer_response.status_code == 200:
                offers = offer_response.json().get(
                    "offers",
                    []
                )

            offer = offers[0] if offers else {}

            final_data.append({

                "sku": sku,

                "title":
                    item.get("product", {})
                        .get("title"),

                "description":
                    item.get("product", {})
                        .get("description"),

                "images":
                    item.get("product", {})
                        .get("imageUrls", []),

                "image":
                    item.get("product", {})
                        .get("imageUrls", [""])[0],

                "quantity":
                    item.get("availability", {})
                        .get("shipToLocationAvailability", {})
                        .get("quantity"),

                "price":
                    offer.get("pricingSummary", {})
                         .get("price", {})
                         .get("value", "N/A"),

                "currency":
                    offer.get("pricingSummary", {})
                         .get("price", {})
                         .get("currency", ""),

                "condition":
                    item.get("condition"),

                "brand":
                    item.get("product", {})
                        .get("aspects", {})
                        .get("Brand", [""])[0]
            })

        print("\n===================================")
        print("SUCCESS")
        print("===================================")

        return jsonify(final_data)

    except requests.exceptions.Timeout:

        print("\nERROR: Request timeout")

        return jsonify({
            "error": "Request timeout"
        }), 500

    except Exception as e:

        print("\nERROR:")
        print(str(e))

        return jsonify({
            "error": str(e)
        }), 500

# ===================================
# RUN APP
# ===================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )