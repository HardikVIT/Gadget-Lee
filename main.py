from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# Route for the index page (optional)
@app.route('/')
def index():
    return render_template('index.html')

# Route for compare.html
@app.route('/compare')
def compare():
    return render_template('compare.html')

# Route to handle form submission and recommendation logic
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json  # Receive data from the form

    # Extract form inputs
    device_type = data['device_type']
    usage_tenure = int(data['usage_tenure'])
    battery_life_needed = int(data['battery_life_needed'])

    # Sample recommendation logic (Replace with your ML logic)
    recommended_device = {
        "Device": f"Recommended {device_type}",
        "Battery_Life_Hours": 24  # Example battery life
    }

    # Send back the recommended device and a dummy plot path
    return jsonify({
        "recommended_device": recommended_device,
        "plot_path": "/static/dummy_battery_plot.png"
    })

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
