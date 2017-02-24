import json
from geopy.geocoders import GoogleV3
from config import google_api_key

input_file = "federal_agency_directory.json"
output_file = "geocoded_directory.json"
cloakroom_file = "cloakroom_network_directory.json"
wh_id = 49743

cabinet_level_ids = [49743, 49229, 49018, 49019, 49022, 49023, 52686, 49028, 49030, 49033, 49035, 48027, 49015, 52668, 49021, 49034]  # Including the White House


def add_geocoordinates_to_directory():
    geolocator = GoogleV3(api_key=google_api_key)

    with open(input_file) as json_data:
        directory = json.load(json_data)

    found_count = 0

    for agency in directory:
        address = agency["Street1"] + ", " + agency["City"] + ", " + agency["Stateter"]
        try:
            location = geolocator.geocode(address, timeout=10)
        except:
            print("Geocoder failed. Found count: %s" % found_count)
        if location is None:
            print("Invalid Location: %s" % address)
        else:
            try:
                geocoordinates = (location.latitude, location.longitude)
                agency["geocode"] = geocoordinates
                found_count += 1
            except:
                print("No coordinates received: %s" % address)

    print("LOCATIONS FOUND: %d" % found_count)

    with open(output_file, 'w') as outfile:  
        json.dump(directory, outfile)

    return directory


def get_top_level_agencies(directory):
    top_level_agencies = []

    for agency in directory:
        if agency["Parent Id"] is None:
            top_level_agencies.append(agency)
            #print(agency["Name"])

    return top_level_agencies


def get_wh_agencies(directory):
    wh_agencies = []

    for agency in directory:
        if agency["Parent Id"] == wh_id:
            wh_agencies.append(agency)
            print(agency["Name"])

    return wh_agencies


def sever_cabinet_agencies_from_wh():
    # This is used for Cloakroom's network hierarchy
    # Cloakroom will treat cabinet departments as independent from the WH
    # Allowing agency users to be distinct from WH offices
    with open(output_file) as json_data:
        directory = json.load(json_data)

    for agency in directory:
        if agency["Agency ID"] in cabinet_level_ids:
            agency["Parent Id"] = None
            agency["Parent Name"] = None
            print(agency["Name"])

    with open(cloakroom_file, 'w') as outfile:  
        json.dump(directory, outfile)

    return directory


# Next step: start from the top level agencies, and work our way down the hierarchy to delete redundant geofences

def remove_redundant_geocodes_and_reorder_data():
    with open(cloakroom_file) as json_data:
        directory = json.load(json_data)

    saved_geolocations = []
    ordered_agencies = []

    tla = get_top_level_agencies(directory)
    tla_ids = []

    for agency in tla:
        tla_ids.append(agency["Agency ID"])

    for agency in directory:
        # First save cabinet level geocodes
        if agency["Agency ID"] in cabinet_level_ids:
            geocode = agency["geocode"]
            if geocode is not None and geocode not in saved_geolocations:
                saved_geolocations.append(geocode)
            elif geocode is not None:
                print("Redundant geocode found for cabinet agency %s %s" % (agency["Name"], agency["geocode"]))
                agency["geocode"] = None
            ordered_agencies.append(agency)

    # Next seed the remaining top level agencies
    for agency in directory:
        if agency["Agency ID"] not in cabinet_level_ids and agency["Agency ID"] in tla_ids:
            geocode = agency["geocode"]
            if geocode is not None and geocode not in saved_geolocations:
                saved_geolocations.append(geocode)
            elif geocode is not None:
                print("Redundant geocode found for %s %s" % (agency["Name"], agency["geocode"]))
                agency["geocode"] = None
            ordered_agencies.append(agency)
    print("Found %d top level agencies." % len(saved_geolocations))

    parent_ids = tla_ids
    child_ids = []
    more_children = True
    while more_children:
        children_found = 0

        for agency in directory:
            if agency["Parent Id"] in parent_ids and agency["Agency ID"] not in child_ids:
                geocode = agency["geocode"]
                if geocode is not None and geocode not in saved_geolocations:
                    saved_geolocations.append(geocode)
                else:
                    agency["geocode"] = None
                ordered_agencies.append(agency)
                child_ids.append(agency["Agency ID"])
                parent_ids.append(agency["Agency ID"])
                children_found += 1

        if children_found == 0:
            more_children = False
            print("Found no more child agencies.")
        else:
            print("Found %d child agencies." % children_found)

    for agency in directory:
        if agency["Agency ID"] not in parent_ids:
            print("Unaccounted agencies: %s" % agency["Name"])

    print("Total agencies in directory: %d" % len(directory))
    print("Total agencies accounted for: %s" % len(parent_ids))
    print("Saved geocodes: %d" % len(saved_geolocations))
    print("Total ordered agencies saved to file: %d" % len(ordered_agencies))

    open(cloakroom_file, 'w').close()

    with open(cloakroom_file, 'w') as outfile:  
        json.dump(ordered_agencies, outfile)


def get_full_domain_from_email(email):
    try:
        return email.split('@')[1]
    except IndexError as e:
        print(e)
        print("Bad email: %s" % email)


def remove_redundant_emails():
    # remove_redundant_geocodes() must be run first

    # REMOVE REDUNDANT DOMAINS!!! Not emails

    with open(cloakroom_file) as json_data:
        directory = json.load(json_data)

    saved_domains = []

    for agency in directory:
        email = agency["Email"]
        if email is not None and email != "":
            domain = get_full_domain_from_email(email)
            if domain is not None and domain not in saved_domains:
                saved_domains.append(domain)
            elif domain is not None and len(domain) > 0:
                print("Redundant email found for cabinet agency %s %s" % (agency["Name"], agency["Email"]))
                agency["Email"] = None

    print("Total agencies in directory: %d" % len(directory))
    print("Saved emails: %d" % len(saved_domains))

    open(cloakroom_file, 'w').close()

    with open(cloakroom_file, 'w') as outfile:  
        json.dump(directory, outfile)


# Main calls the entire massager in order, including GoogleV3
def main():
    add_geocoordinates_to_directory()
    sever_cabinet_agencies_from_wh()
    remove_redundant_geocodes_and_reorder_data()
    remove_redundant_emails()
