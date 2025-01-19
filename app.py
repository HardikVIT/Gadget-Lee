from flask import Flask, request, render_template, jsonify
from flask_cors import CORS  
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import os
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

app = Flask(__name__)
CORS(app)

data = pd.read_csv('device_comparison_data.csv')

df = pd.DataFrame(data)

# Prepare data for MLP

X = pd.get_dummies(df[['Type', 'Rating', 'Software_Performance']], drop_first=True)  # One-hot encoding
y = df['Battery_Life_Hours']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the MLP model
mlp = MLPRegressor(hidden_layer_sizes=(10, 5), max_iter=1000, random_state=42)
mlp.fit(X_train, y_train)



@app.route('/')
def home():
    return render_template('compare.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    form_data = request.json
    device_type = form_data.get('device_type')
    battery_life_needed = int(form_data.get('battery_life_needed'))

    compare_list = form_data.get('compare_list', [])

    compare_devices = df[df['Device'].isin([item['title'] for item in compare_list])]

    predicted_batteries = []

    for index, row in compare_devices.iterrows():

        input_data = pd.DataFrame({
            'Type': [row['Type']],
            'Rating': [row['Rating']],
            'Software_Performance': [row['Software_Performance']]
        })
        
        input_data_encoded = pd.get_dummies(input_data, drop_first=True)
        input_data_encoded = input_data_encoded.reindex(columns=X.columns, fill_value=0)
        predicted_battery_life = mlp.predict(input_data_encoded.values.reshape(1, -1))[0]
        predicted_batteries.append({
            'Device': row['Device'],
            'Predicted_Battery_Life': predicted_battery_life,
            'Actual_Battery_Life': row['Battery_Life_Hours']
        })

    # Comparison
    closest_device = None
    smallest_difference = float('inf')

    for device in predicted_batteries:
        difference = abs(device['Predicted_Battery_Life'] - battery_life_needed)
        
        if difference < smallest_difference:
            smallest_difference = difference
            closest_device = device

    if closest_device:
        recommended_device = {
            'Device': closest_device['Device'],
            'Predicted_Battery_Life': closest_device['Predicted_Battery_Life'],
            'Actual_Battery_Life': closest_device['Actual_Battery_Life'],
            'Difference': smallest_difference
        }
    else:
        recommended_device = {'Message': 'No suitable devices found.'}


    # Battery life comparison plot
    plt.figure(figsize=(8, 5))
    compare_devices.plot(kind='bar', x='Device', y='Battery_Life_Hours', legend=False, color='skyblue')
    plt.ylabel('Battery Life (Hours)')
    plt.title('Battery Life Comparison')
    battery_plot_path = os.path.join(app.static_folder, 'battery_life.png')
    plt.savefig(battery_plot_path)
    plt.close()

    # Software performance comparison plot
    plt.figure(figsize=(8, 5))
    compare_devices.plot(kind='bar', x='Device', y='Software_Performance', legend=False, color='lightgreen')
    plt.ylabel('Performance Score')
    plt.title('Software Performance Comparison')
    performance_plot_path = os.path.join(app.static_folder, 'software_performance.png')
    plt.savefig(performance_plot_path)
    plt.close()

    return jsonify({
        'recommended_device': recommended_device,
        'battery_plot_path': 'static/battery_life.png',
        'software_plot_path': 'static/software_performance.png'
    })


if __name__ == '__main__':
    app.run(debug=True)
