from flask import Flask, render_template, request
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Call the scraping function
    data = scrape_social_media_users()

    # Check if data is a DataFrame before proceeding
    if isinstance(data, pd.DataFrame) and not data.empty:
        # Save the scraped data to a CSV file
        data.to_csv('data/social_media_users.csv', index=False)

        # Create a bar chart using Plotly
        if 'Platform' in data.columns and 'Users' in data.columns:
            fig = px.bar(data, x='Platform', y='Users', title='Social Media Users by Platform')

            # Convert the Plotly figure to an HTML div string
            graph_html = pio.to_html(fig, full_html=False)

            # Pass the graph_html variable to the template
            return render_template('index.html', graph_html=graph_html)
        else:
            return "Data does not contain expected columns."
    else:
        # Handle the error if data is not a DataFrame or is empty
        return "Scraping failed, no valid data returned."

def scrape_social_media_users():
    # URL for scraping
    url = 'https://backlinko.com/social-media-users'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specific table by class
    table = soup.find('table', class_='table table-primary table-striped table-hover')

    # Check if the table is found
    if table is None:
        raise ValueError("Could not find the table with the specified class. Please check the HTML structure.")

    # Initialize a list to store the table data
    data = []

    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th')]

    # Extract table rows
    rows = table.find_all('tr')
    for row in rows[1:]:
        values = [value.text.strip() for value in row.find_all('td')]
        data.append(values)

    # Create a DataFrame from the scraped data
    df = pd.DataFrame(data, columns=headers)
    
    return df

if __name__ == '__main__':
    app.run(debug=True)
