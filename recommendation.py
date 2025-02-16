import pandas as pd
import flask
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the dataset
csv_file_path = "products.csv"  # Ensure this matches your file name
df = pd.read_csv(csv_file_path)

# Convert ingredient strings to lists
df["clean_ingreds"] = df["clean_ingreds"].apply(lambda x: eval(x) if isinstance(x, str) else [])

# Define beneficial ingredients for different skin concerns
skin_concern_ingredients = {
    "dry": ["hyaluronic acid", "glycerin", "ceramides", "squalane"],
    "oily": ["niacinamide", "salicylic acid", "zinc", "clay"],
    "redness": ["azelaic acid", "allantoin", "centella", "green tea"],
    "pimples": ["benzoyl peroxide", "salicylic acid", "tea tree oil"],
    "openPores": ["niacinamide", "retinol", "clay", "witch hazel"]
}

def convert_price_to_inr(price):
    try:
        # Fetch exchange rate from an API (Replace 'your_api_key' with a valid one)
        exchange_rate = 83  # Static value (1 USD = 83 INR) or fetch dynamically
        price_value = float(price.replace("₹", "").strip())  # Remove symbols & convert to float
        return f"₹{round(price_value * exchange_rate, 2)}"
    except:
        return price  # If conversion fails, return original price

def recommend_products(skin_issues):
    """
    Recommend products based on the user's skin concerns.
    :param skin_issues: List of detected skin concerns (e.g., ["oily", "pimples"])
    :return: List of recommended products
    """
    relevant_products = []
    
    for concern in skin_issues:
        if concern in skin_concern_ingredients:
            beneficial_ingredients = skin_concern_ingredients[concern]
            
            # Filter products that contain beneficial ingredients
            filtered_products = df[df["clean_ingreds"].apply(lambda ingredients: any(ing in ingredients for ing in beneficial_ingredients))]
            
            # Append results
            relevant_products.extend(filtered_products.to_dict(orient="records"))

    # Remove duplicates and limit recommendations
    unique_products = {prod["product_name"]: prod for prod in relevant_products}.values()

    for product in unique_products:
        product["price"] = convert_price_to_inr(product["price"])
    
    return list(unique_products)[:10]  # Return top 10 recommendations

@app.route("/recommend", methods=["POST"])
def recommend():
    """
    API endpoint to get skincare product recommendations.
    Expects JSON input: {"skin_issues": ["oily", "redness"]}
    """
    try:
        data = request.get_json()
        skin_issues = data.get("skin_issues", [])
        
        recommendations = recommend_products(skin_issues)
        
        return jsonify({"recommendations": recommendations})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002, debug=True)
