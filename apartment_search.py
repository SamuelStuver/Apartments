from requests_html import HTMLSession
import re
import csv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="apartment_search")

def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def get_coords(address):
    location = geolocator.geocode(address)
    #print((location.latitude, location.longitude))
    if location:
        return (location.latitude, location.longitude)
    else:
        return (-1, -1)

def dist_between_coords(coords1, coords2):
    return geodesic(coords1, coords2).miles

def get_city_from_address(address):
    regex = r"(.*), ([A-Za-z]*), (.*)"
    try:
        return re.search(regex, address).group(2)
    except:
        return "Unavailable"

def header_handler(header):
    regex = r"(.*)\n(.*)"
    title = re.search(regex, header.text).group(1)
    address = re.search(regex, header.text).group(2)
    coords = get_coords(address)
    dist = dist_between_coords(coords, work_coords)
    real_city = get_city_from_address(address)
    return {"title":title, "address":address, "coords":coords, "distance":dist, "city":real_city}

def content_handler(content):
    rent = content.find('span.altRentDisplay', first=True).text
    unit_label = content.find('span.unitLabel', first=True).text
    availability = content.find('span.availabilityDisplay', first=True).text
    try:
        phone = content.find('div.contactInfo', first=True).text
    except AttributeError:
        phone = ""
    # Get the max and min rent
    try:
        regex = r"(.*) - (.*)"
        min_rent = re.search(regex, rent).group(1).replace("$","").replace(",","")
        max_rent = re.search(regex, rent).group(2).replace("$","").replace(",","")

        min_rent = int(min_rent)
        max_rent = int(max_rent)
    except AttributeError:
        min_rent = max_rent = int(rent.replace("$","").replace(",",""))

    return {"min_rent":min_rent, "max_rent":max_rent, "unit_label":unit_label, "availability":availability, "phone":phone}

cities = ["broomfield", "westminster", "louisville"]

work_coords = get_coords("1380 Forest Park Cir, Lafayette, CO 80026")
print(work_coords)

results = []
for page in range(1, 3):
    for city in cities:
        session = HTMLSession()
        r = session.get(f'https://www.apartments.com/{city}-co/1-bedrooms-under-1500/{page}/')
        html = r.html

        # Get the cards
        articles = html.find('article')

        for article in articles:
            # Get the title and address of the card
            header = article.find('header.placardHeader', first=True)
            if header:
                header_dict = header_handler(header)

            # Get the content of the card
            content = article.find('div.infoPadding', first=True)
            if content:
                content_dict = content_handler(content)

            result = merge_dicts(header_dict, content_dict)
            results.append(result)

            print(f"Title: {result['title']}")
            print(f"City: {result['city']}")
            print(f"Address: {result['address']}")
            print(f"Coordinates: {result['coords']}")
            print(f"Distance (mi): {result['distance']}")
            print(f"Unit: {result['unit_label']}")
            print(f"Rent: {result['min_rent']} - {result['max_rent']}")
            print(f"Avail: {result['availability']}")
            print(f"Contact: {result['phone']}")
            print()

with open('apartments.csv', 'w', newline='') as outfile:
    outputDictWriter = csv.DictWriter(outfile, results[0].keys())
    outputDictWriter.writeheader()

    for result in results:
        outputDictWriter.writerow(result)

print("Done.")
