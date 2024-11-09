from flask import Flask, render_template, jsonify
import pandas as pd
import plotly.express as px
import plotly.io as pio
import glob

app = Flask(__name__)

# Load data from multiple CSV files and concatenate
data_files = glob.glob('data/*.csv')  # Adjust directory if necessary
data_frames = [pd.read_csv(file, encoding='ISO-8859-1') for file in data_files]
combined_data = pd.concat(data_frames, ignore_index=True)

# Ensure `Sent Date` column is parsed correctly
combined_data['Sent Date'] = pd.to_datetime(combined_data['Sent Date'], errors='coerce')
combined_data.dropna(subset=['Sent Date'], inplace=True)  # Drop rows with invalid dates

# Helper function to generate popular items chart
def generate_sales_chart():
    if 'Parent Menu Selection' in combined_data.columns:
        # Group by `Parent Menu Selection` and count occurrences
        popular_items = combined_data['Parent Menu Selection'].value_counts()
        fig = px.bar(popular_items, x=popular_items.index, y=popular_items.values,
                     labels={'x': 'Menu Item', 'y': 'Order Count'},
                     title="Popular Items")
        return pio.to_json(fig)
    else:
        return jsonify({'error': 'Parent Menu Selection column missing'})

# Helper function to generate monthly order trends chart
def generate_trends_chart():
    if 'Order #' in combined_data.columns and 'Sent Date' in combined_data.columns:
        combined_data['Month'] = combined_data['Sent Date'].dt.to_period('M')
        monthly_trends = combined_data.groupby('Month')['Order #'].nunique()
        fig = px.line(monthly_trends, x=monthly_trends.index.astype(str), y=monthly_trends.values,
                      labels={'x': 'Month', 'y': 'Number of Orders'},
                      title="Monthly Order Trends")
        return pio.to_json(fig)
    else:
        return jsonify({'error': 'Order # or Sent Date column missing'})

# Helper function to generate meal preparation efficiency chart
def generate_efficiency_chart():
    if 'Option Group Name' in combined_data.columns:
        efficiency_data = combined_data['Option Group Name'].value_counts()
        fig = px.bar(efficiency_data, x=efficiency_data.index, y=efficiency_data.values,
                     labels={'x': 'Option Group', 'y': 'Frequency'},
                     title="Meal Preparation Efficiency")
        return pio.to_json(fig)
    else:
        return jsonify({'error': 'Option Group Name column missing'})

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sales')
def sales():
    chart_json = generate_sales_chart()
    return chart_json

@app.route('/trends')
def trends():
    chart_json = generate_trends_chart()
    return chart_json

@app.route('/efficiency')
def efficiency():
    chart_json = generate_efficiency_chart()
    return chart_json

if __name__ == '__main__':
    app.run(debug=True)
