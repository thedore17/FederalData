import json
from geopy.geocoders import GoogleV3

input_file = "federal_agency_directory.json"
output_file = "massaged_directory.json"


def massage_federal_directory():
    geolocator = GoogleV3()

    with open(input_file) as json_data:
        directory = json.load(json_data)

    found_count = 0

    for agency in directory:
        address = agency["Street1"] + ", " + agency["City"] + ", " + agency["Stateter"]
        location = geolocator.geocode(address, timeout=10)
        if location is None:
            print("Invalid Location: %s" % address)
        else:
            try:
                geocoordinates = (location.latitude, location.longitude)
                agency["Geocoordinates"] = geocoordinates
                found_count += 1
            except:
                print("No coordinates received: %s" % address)

    print("LOCATIONS FOUND: %d" % found_count)

    with open(output_file, 'w') as outfile:  
        json.dump(directory, outfile)

