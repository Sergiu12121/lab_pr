import requests
from bs4 import BeautifulSoup

# Define the URL
url = "https://999.md/ro/list/transport/cars"

# Make the HTTP GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements that contain product names and prices
    # Inspect the website to find the right HTML tags and classes
    products = soup.find_all('div', class_='ads-list-photo-item-title')  # This class might need adjustment based on actual site structure

    # Iterate over products and extract names and prices
    for product in products:
        name = product.get_text(strip=True)  # Extract the text content for the product name
        price = product.find_next('div', class_='ads-list-photo-item-price').get_text(strip=True)  # Adjust class for price as necessary
        print(f"Product Name: {name}, Price: {price}")
else:
    print(f"Request failed with status code: {response.status_code}")
