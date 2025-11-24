from flask import Flask, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/data')
def get_mock_data():
    # Chaos Mode: 15% chance of returning HTTP 500 error
    if random.random() < 0.15:
        return jsonify({"error": "Internal Server Error - Chaos Mode Activated"}), 500

    # Dynamic Data Generation
    product_id = f"sku_{random.randint(1000, 9999)}"
    stock_level = random.randint(0, 1000)
    
    warehouse_locations = ["Zone-A", "Zone-B", "Zone-C", "Zone-D", "Warehouse-X", "Warehouse-Y", "Storage-1", "Storage-2"]
    warehouse_location = random.choice(warehouse_locations)
    
    # Generate a random future date for next_shipment
    today = datetime.now()
    future_days = random.randint(1, 365) # shipment within the next year
    next_shipment_date = today + timedelta(days=future_days)
    next_shipment = next_shipment_date.strftime("%Y-%m-%d")
    
    statuses = ["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK", "BACKORDERED", "SHIPPING", "DELIVERED"]
    status = random.choice(statuses)
    
    dimensions = {
        "h": random.randint(5, 100),
        "w": random.randint(5, 100),
        "l": random.randint(5, 100)
    }

    response_data = {
        "product_id": product_id,
        "stock_level": stock_level,
        "warehouse_location": warehouse_location,
        "next_shipment": next_shipment,
        "status": status,
        "dimensions": dimensions
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)