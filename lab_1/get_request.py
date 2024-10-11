import requests

# Define the URL
url = "https://999.md/ro/list/transport/cars"

# Make the HTTP GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    print("HTML content:")
    print(response.text)  # Print the HTML content/body
else:
    print(f"Request failed with status code: {response.status_code}")
