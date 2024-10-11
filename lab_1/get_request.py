import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from functools import reduce

# URL of the 999.md page for cars
url = "https://999.md/ro/list/transport/cars"

# Perform the HTTP GET request with headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Exchange rates (assumed values for conversion)
EUR_TO_MDL = 19.0
USD_TO_MDL = 17.0

# Check if the request was successful
if response.status_code == 200:
    print("Request was successful!")
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract car names, years, prices, and links
    car_listings = []

    # Find all the elements containing car details
    car_elements = soup.find_all('li', class_='ads-list-photo-item')

    # Loop through each element and extract the name, year, price, and link
    for car in car_elements:
        name_element = car.find('div', class_='ads-list-photo-item-title')
        if name_element:
            full_name = name_element.get_text(strip=True)
            name_parts = full_name.split(', ')
            name = name_parts[0] if len(name_parts) > 0 else 'No name'
            year = name_parts[1].replace('an', '').strip() if len(name_parts) > 1 else 'No year'
        else:
            name = 'No name'
            year = 'No year'
        
        # Extract the price and identify the currency
        price_element = car.find('div', class_='ads-list-photo-item-price')
        if price_element:
            price_text = price_element.get_text(strip=True)
            if '€' in price_text:
                currency = 'EURO'
                price = float(price_text.split('€')[0].strip().replace(' ', '').replace(',', ''))
            elif '$' in price_text:
                currency = 'USD'
                price = float(price_text.split('$')[0].strip().replace(' ', '').replace(',', ''))
            elif 'MDL' in price_text or 'lei' in price_text:
                currency = 'MDL'
                price = float(price_text.split(' ')[0].strip().replace(' ', '').replace(',', ''))
            else:
                currency = 'Unknown'
                price = 0.0
        else:
            price = 0.0
            currency = 'Unknown'
        
        # Extract the product link
        link_element = car.find('a', href=True)
        link = f"https://999.md{link_element['href']}" if link_element else 'No link'

        # Add the extracted information to the list, placing 'Link' as the last item
        car_listings.append({
            'Name': name,
            'Year': year,
            'Price': price,
            'Currency': currency,
            'Link': link
        })

    # Map prices to EUR (if not in EUR) or convert EUR to MDL
    def map_to_eur_or_mdl(car):
        if car['Currency'] == 'USD':
            car['Price_EUR'] = car['Price'] / USD_TO_MDL * EUR_TO_MDL
        elif car['Currency'] == 'MDL':
            car['Price_EUR'] = car['Price'] / EUR_TO_MDL
        elif car['Currency'] == 'EURO':
            car['Price_EUR'] = car['Price']  # Price already in EUR
        else:
            car['Price_EUR'] = 0.0  # Default for unknown currency
        return car

    mapped_cars = list(map(map_to_eur_or_mdl, car_listings))

    # Define a price range (e.g., between 1000 EUR and 20000 EUR)
    price_min = 1000
    price_max = 20000

    # Filter the cars within the price range
    filtered_cars = list(filter(lambda car: price_min <= car['Price_EUR'] <= price_max, mapped_cars))

    # Use reduce to calculate the sum of prices of the filtered cars
    total_sum_eur = reduce(lambda acc, car: acc + car['Price_EUR'], filtered_cars, 0)

    # Add the total sum and UTC timestamp to the final data structure
    final_data = {
        'Filtered_Products': filtered_cars,
        'Total_Sum_EUR': total_sum_eur,
        'Timestamp_UTC': datetime.utcnow().isoformat()
    }

    # JSON serialization function
    def serialize_to_json(data):
        if isinstance(data, dict):
            json_str = '{'
            json_str += ', '.join(f'"{key}": {serialize_to_json(value)}' for key, value in data.items())
            json_str += '}'
        elif isinstance(data, list):
            json_str = '['
            json_str += ', '.join(serialize_to_json(item) for item in data)
            json_str += ']'
        elif isinstance(data, str):
            json_str = f'"{data}"'
        elif isinstance(data, (int, float)):
            json_str = str(data)
        elif data is None:
            json_str = 'null'
        else:
            raise TypeError(f"Type {type(data)} not serializable")
        return json_str

    # XML serialization function
    def serialize_to_xml(data, root_tag='data'):
        xml_str = f'<{root_tag}>'
        if isinstance(data, dict):
            for key, value in data.items():
                xml_str += serialize_to_xml(value, root_tag=key)
        elif isinstance(data, list):
            for item in data:
                xml_str += serialize_to_xml(item, root_tag='item')
        elif isinstance(data, str):
            xml_str += f'{data}'
        elif isinstance(data, (int, float)):
            xml_str += str(data)
        elif data is None:
            xml_str += ''
        else:
            raise TypeError(f"Type {type(data)} not serializable")
        xml_str += f'</{root_tag}>'
        return xml_str

    # Serialize to JSON and XML
    json_result = serialize_to_json(final_data)
    xml_result = serialize_to_xml(final_data, root_tag='FinalData')

    # Write the serialized results to files
    with open('car_listings.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_result)
    with open('car_listings.xml', 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_result)

    # Print confirmation of file creation
    print("Serialized JSON saved to car_listings.json")
    print("Serialized XML saved to car_listings.xml")

    # Optionally, save the filtered data to a CSV with 'Link' as the last column
    filtered_df = pd.DataFrame(filtered_cars)
    filtered_df = filtered_df[['Name', 'Year', 'Price_EUR', 'Currency', 'Link']]
    filtered_df.to_csv('filtered_car_listings.csv', index=False)
    print("Filtered car listings saved to filtered_car_listings.csv")
    
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
