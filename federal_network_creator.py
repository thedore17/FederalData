from directory_massager import cloakroom_file, get_top_level_agencies, cabinet_level_ids
import json


class Network:
    # Base class for Cloakroom Networks
    def __init__(self, name, numeric_id):
        self.name = name
        self.numeric_id = numeric_id
        self.domains = []
        self.locations = []

    def add_domain(self, domain):
        self.domains.append(domain)

    def add_location(self, geocode):
        self.locations.append(geocode)


def get_full_domain_from_email(email):
        try:
            return email.split('@')[1]
        except IndexError as e:
            print(e)
            print("Bad email: %s" % email)


def get_all_domains_from_email(email):
    try:
        user_domain = email.split('@')[1]
        separator = "."
        domain_slices = user_domain.split(separator)
        tld = domain_slices[-1]
        del domain_slices[-1]
        domains = []
        for element in reversed(domain_slices):
            tld = element + "." + tld
            domains.append(tld)
        return domains
    except IndexError as e:
        print(e)
        print("Bad email: %s" % email)
        return None


def get_network_id_prefix():
    numerals = [ord(char) - 96 for char in "usfederalagency".lower()]
    prefix = ""
    for numeral in numerals:
        prefix += str(numeral)
    return prefix


def simulate_network_creation():
    with open(cloakroom_file) as json_data:
        directory = json.load(json_data)

    saved_networks = []

    for agency in directory:
        network_id = get_network_id_prefix() + str(agency["Agency ID"])
        email = agency["Email"]
        geocode = agency["geocode"]
        new_network = Network(name=agency["Name"].lower(), numeric_id=network_id)
        valid = False

        if geocode is not None:
                new_network.add_location(geocode)
                valid = True

        if email == "":
            email = None

        if email is not None:
            if agency["Agency ID"] in cabinet_level_ids:
                domains = get_all_domains_from_email(email)
                if domains is None:
                    print("Agency with bad email: %s" % new_network.name)
                else:
                    new_network.domains = get_all_domains_from_email(email)
                    valid = True

            else:
                domain = get_full_domain_from_email(email)
                if domain is None:
                    print("Agency with bad email: %s" % new_network.name)
                else:
                    new_network.add_domain(domain)
                    valid = True

        if valid:
            saved_networks.append(new_network)

    return saved_networks

# General GAE process
# 1 Query for networks in datastore for agency's email domains
# 2 If original

# Lastly, loop through all users and delete their network assignments (But don't delete the network entities themselves)
# Next time the user logs on or refreshes the lobby or live feed, they'll be assigned a new network based on their stored email address or geofence?