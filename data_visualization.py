import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from datetime import timedelta
from flask import Flask, jsonify, send_file, Response, render_template, url_for, request
from io import BytesIO
import os

app = Flask(__name__, static_url_path='/static')

app.config['UPLOAD_FOLDER'] = 'static/uploads'

upload_folder = app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

class visual:
    def  __init__(self):
        self.data_type = 'a'
        self.data1 = 'a'
        self.data2 = 'a'
        self.df = pd.read_csv("weatherHistory.csv")
        self.weather = 0
        self.filename = 'plot.png'
    def update_data(self, updated_type, updated_data2):
        self.data_type = updated_type
        self.data2 = updated_data2
    def to_type(self):
        self.df['Weather Conidition'] = self.df['Summary']
        self.df['Temperature (C)'] = self.df['Temperature (C)'].astype('float')
        self.df['Apparent Temperature (C)'] = self.df['Apparent Temperature (C)'].astype('float')
        self.df['Humidity'] = self.df['Humidity'].astype('float')
        self.df['Wind Speed (km/h)'] = self.df['Wind Speed (km/h)'].astype('float')
        self.df['Wind Bearing (degrees)'] = self.df['Wind Bearing (degrees)'].astype('int')
        self.df['Visibility (km)'] = self.df['Visibility (km)'].astype('float')
        self.df['Pressure (millibars)'] = self.df['Pressure (millibars)'].astype('float')
        self.df['Precip Type'].fillna( self.df['Precip Type'].value_counts().index[0], inplace=True)
        self.df['Formatted Date'] = pd.to_datetime(self.df['Formatted Date'], utc=True)
        self.weather = self.df['Summary'].value_counts().reset_index()
        self.weather.columns=['Weather', 'Count']
        self.df['Year'] = self.df['Formatted Date'].dt.year
        self.df['Month'] = self.df['Formatted Date'].dt.month
        self.df['Day'] = self.df['Formatted Date'].dt.day
        self.df['Time'] = self.df['Formatted Date'].dt.time
        self.df['Time'] = self.df['Time'].astype('string')
        self.ym = self.df[(self.df['Day'] == 1) & (self.df['Time'] == '00:00:00')]
    def generate(self):
        if os.path.exists("static/uploads/_plot.png"):
            os.remove("static/uploads/plot.png")
        if self.data_type == "barplot":
            plt.figure(figsize=(10, 6))
            plt.xticks(rotation=90)
            title = "Barplot of maximum " + self.data2 + " for certain " + "Weather Condition"
            plt.title(title)
    
            sns.barplot(x=self.df['Weather Conidition'], y=self.df[self.data2], hue=self.df['Weather Conidition'], legend=False, palette=sns.color_palette("Set2"))
            plt.tight_layout()
            
            self.filename = 'plot.png'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], self.filename)
            plt.savefig(filepath)
            plt.close()
        elif self.data_type == "heatmap":
            title = "Heatmap of" + self.data2 + " from 2006 to 2016"
            plt.title(title)
            heat = (self.ym.pivot(index='Month', columns='Year', values = self.data2))
            sns.heatmap(heat, annot=True, linewidths=.5)
            plt.tight_layout()
            
            self.filename = 'plot.png'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], self.filename)
            plt.savefig(filepath)
            plt.close()
        elif self.data_type == "lineplot":
            title = "Line plot of " + self.data2 + " from 2006 to 2016"
            plt.title(title)
            sns.lineplot(x="Formatted Date", y=self.data2, data=self.ym)
            plt.tight_layout()

            self.filename = 'plot.png'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], self.filename)
            plt.savefig(filepath)
            plt.close()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/weather-count')
def weather_count():
    # Generating Weather Count data
    statistic = visual()
    weather_data = statistic.df['Summary'].value_counts().reset_index()
    weather_data.columns = ['Weather', 'Count']
    
    # Render the HTML template and pass the weather data to it
    return render_template('weather_count.html', weather_data=weather_data.to_dict(orient='records'))


@app.route('/weather-humidity-plot', methods=['GET', 'POST'])
def weather_humidity_plot(): 
    img = visual()
    img.to_type()
    img.generate()
    
    if request.method=='POST':
        data_type = request.form.get('new_type')
        data2 = request.form.get('new_data2')
        img.update_data(data_type, data2)
        img.generate()
        
    # Pass the image path to the HTML template for rendering
    return render_template('weather_humidity_plot.html', image_path=url_for('static', filename='uploads/' + img.filename))

if __name__ == '__main__':

    app.run(debug=True, threaded=False)