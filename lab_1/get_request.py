import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Define the base URL
base_url = "https://999.md"
url = "https://999.md/ro/list/transport/cars"

# Data structure to store validated product data
products_data = []

# Function to validate the price is not empty
def validate_price(price):
    return bool(price and price.strip())

# Function to validate the product link is a valid URL
def validate_link(link):
    parsed_url = urlparse(link)
    return all([parsed_url.scheme, parsed_url.netloc])

# Make the HTTP GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements that contain product names, prices, and links
    products = soup.find_all('div', class_='ads-list-photo-item-title')  # Adjust this based on the site's structure

    # Iterate over products and extract names, prices, and links (limit to 5 products)
    for index, product in enumerate(products):
        if index >= 5:
            break

        name = product.get_text(strip=True)  # Extract the text content for the product name
        price = product.find_next('div', class_='ads-list-photo-item-price').get_text(strip=True)  # Adjust class for price as necessary

        # Extract the product link
        link_tag = product.find('a')
        if link_tag and 'href' in link_tag.attrs:
            product_link = base_url + link_tag['href']  # Construct full URL
            
            # Validate price and link before storing
            if validate_price(price) and validate_link(product_link):
                # Store validated product data
                product_info = {
                    "name": name,
                    "price": price,
                    "link": product_link
                }
                products_data.append(product_info)

                print(f"Stored Product: {product_info}")

                # Scrape the product link for additional information
                product_response = requests.get(product_link)
                if product_response.status_code == 200:
                    product_soup = BeautifulSoup(product_response.text, 'html.parser')

                    # Extract additional information, like product description
                    description = product_soup.find('div', class_='product-description')  # Adjust based on site structure
                    if description:
                        description_text = description.get_text(strip=True)
                        print(f"Description: {description_text}")
                    else:
                        print("Description not found.")
                else:
                    print(f"Failed to retrieve product page: {product_response.status_code}")
            else:
                print(f"Validation failed for product: Name: {name}, Price: {price}, Link: {product_link}")
        else:
            print("Link not found for this product.")

else:
    print(f"Request failed with status code: {response.status_code}")

# Print out the validated products data
print("\nValidated Products Data:")
for product in products_data:
    print(product)
