import requests
from bs4 import BeautifulSoup

# Define the base URL
base_url = "https://999.md"
url = "https://999.md/ro/list/transport/cars"

# Make the HTTP GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements that contain product names, prices, and links
    products = soup.find_all('div', class_='ads-list-photo-item-title')  # Adjust this based on the site's structure

    # Iterate over products and extract names, prices, and links
    for product in products:
        name = product.get_text(strip=True)  # Extract the text content for the product name
        price = product.find_next('div', class_='ads-list-photo-item-price').get_text(strip=True)  # Adjust class for price as necessary

        # Extract the product link
        link_tag = product.find('a')
        if link_tag and 'href' in link_tag.attrs:
            product_link = base_url + link_tag['href']  # Construct full URL
            print(f"Product Name: {name}, Price: {price}, Link: {product_link}")

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
            print("Link not found for this product.")

else:
    print(f"Request failed with status code: {response.status_code}")
