import json
import csv
import time
import datetime
import os

import requests
from dotenv import load_dotenv


def export_to_csv(activities):
    ''' Exports my runs to a CSV file named `output.csv`.
    The following fomat is used:
    <name of the run>,<distance in KM>,<pace>,<date>
    Example:
    Maheu #31,5.8,05:02,2020-07-12
    '''
    with open('output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        for activity in activities:
            # Calculate the pace
            pace = time.strftime("%M:%S", time.gmtime(activity['moving_time'] / activity['distance'] * 1000))
            # Format the date (I don't care about the time of the day)
            date = datetime.datetime.strptime(activity['start_date_local'].split('T')[0], '%Y-%m-%d').date()
            writer.writerow([
                activity['name'],
                round(activity['distance'] / 1000, 2), # Convert from meters to kilometers
                pace,
                date
            ])


def get_access_token() -> str:
    ''' Queries the Strava API to refresh the access token.
    '''
    auth_url = 'https://www.strava.com/oauth/token'
    auth_payload = {
        'client_id': os.getenv('STRAVA_CLIENT_ID'),
        'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
        'grant_type': 'refresh_token',
        'refresh_token': os.getenv('STRAVA_REFRESH_TOKEN'),
        'f': 'json',
    }
    print('Requesting a new access token from Strava')
    auth_resp = requests.post(auth_url, data=auth_payload, verify=False)
    return auth_resp.json()['access_token']


def get_activities(access_token: str, per_page: int = 100):
    ''' Queries Strava, and return a list of all my activities.
    '''
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

    # TODO: Add paging logic
    print('Gathering the activities from Strava')
    activities_resp = requests.get(f'{activities_url}?per_page={per_page}',
                                   headers={'Authorization': f'Bearer {access_token}'})

    activities_json = activities_resp.json()
    assert len(activities_json) <= 100, 'You need to implement the paging mechanism!'

    return activities_json


#with open('data.json', 'r') as f:
    #activities = json.load(f)
#pprint(activities)



if __name__ == '__main__':
    # Load environment variables
    load_dotenv()

    # Get new access token and query the activities
    access_token = get_access_token()
    activities = get_activities(access_token)

    # Find my 'Maheu' runs
    maheu_runs = [x for x in activities if 'maheu' in x['name'].lower()]
    print(f'Found {len(maheu_runs)} activities containing the "Maheu" keyword')

    export_to_csv(maheu_runs)