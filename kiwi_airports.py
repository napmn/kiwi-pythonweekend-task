import requests
import argparse
import json
import sys
import csv


def parse_options():
    """
    Parses input options for the script.

    Returns
    -------
    arparse.Namespace
        parsed options
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--cities', action='store_true')
    parser.add_argument('--coords', action='store_true')
    parser.add_argument('--iata', action='store_true')
    parser.add_argument('--names', action='store_true')
    parser.add_argument('--full', action='store_true')
    parsed_options = parser.parse_args()
    return parsed_options


def get_airports(iso_country_code, limit):
    """
    Gets details about airports of given country from
    Kiwi locations API.

    Parameters
    ----------
    iso_country_code: str
        ISO3166 location code
    limit: int
        max results to retrieve from the API

    Returns
    -------
    dict
        parsed json response

    Raises
    ------
    Exception
        raised when api responds with status code different than 2xx
    """
    response = requests.get('https://api.skypicker.com/locations',
            params={
                'type': 'subentity',
                'term': iso_country_code,
                'location_types': 'airport',
                'limit': limit
            })
    if not response.ok:
        raise(Exception('Could not fetch data from kiwi locations API.'))
    return json.loads(response.text)
    

def output_airports(json_response, parsed_options):
    """
    Outputs airports in csv format to stdout.

    Parameters
    ----------
    json_response: dict
        parsed json response from API
    parsed_options: argparse.Namespace
        parsed input options for the script
    """
    fieldnames = get_fieldnames(parsed_options)
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames,
            extrasaction='ignore')
    writer.writeheader()
    for i, airport in enumerate(json_response['locations']):
        row = create_airport_row(airport)
        writer.writerow(row)


def create_airport_row(airport):
    """
    Extracts necessary data from the json data about airport
    returned from API.

    Parameters
    ----------
    airport: dict
        one airport location from the API response
    
    Returns
    -------
    dict
        row that contains parsed data of the airport
    """
    row = {
        'name': airport['name'],
        'city': airport['city']['name'],
        'lon': airport['location']['lon'],
        'lat': airport['location']['lat'],
        'iata': airport['code']
    }
    return row


def get_fieldnames(parsed_options):
    """
    Creates list of fieldnames for the csv output
    by the input options of the script. If no option
    were specified, only name column will be in fieldnames. 
    
    Parameters
    ----------
    parsed_options: argparse.Namespace
        parsed input options of the script

    Returns
    -------
    list
        list of fieldnames(header) for the csv output
    """
    fieldnames = []
    if True not in vars(parsed_options).values():
        return ['name']
    if parsed_options.full:
        return ['name', 'city', 'lon', 'lat', 'iata']
    if parsed_options.names:
        fieldnames.append('name')
    if parsed_options.cities:
        fieldnames.append('city')
    if parsed_options.coords:
        fieldnames.extend(['lon', 'lat'])
    if parsed_options.iata:
        fieldnames.append('iata')
    return fieldnames


if __name__ == '__main__':
    parsed_options = parse_options()
    try:
        json_response = get_airports('GB', 100)
        output_airports(json_response, parsed_options)
    except Exception as e:
        print(str(e))
    
    
    