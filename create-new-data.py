import json
import os
from datetime import timedelta, datetime
from io import StringIO
import pandas as pd
import requests


def write(file, key, time):
    config_file = open(file, 'r')

    config_file_json = json.load(config_file)
    config_file_json[key] = time

    config_file.close()
    config_file = open(file, 'w')

    json.dump(config_file_json, config_file, ensure_ascii=False, indent=4)

    config_file.close()


def export_csv(endpoint, time, output_dir):
    print(endpoint, output_dir)
    r = requests.get(endpoint)
    df = pd.read_csv(StringIO(r.text))
    df = df.drop(["FIPS", "Admin2", "Active", "Combined_Key"], axis=1)
    df = df.rename(
        columns={"Province_State": "Province/State", "Country_Region": "Country/Region", "Last_Update": "Last Update",
                 "Lat": "Latitude", "Long_": "Longitude"})

    columns = ['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered', 'Latitude',
               'Longitude']
    df = df[columns]

    kvmap = {}
    for i in range(len(df)):
        province = df.loc[i, 'Province/State']
        country = df.loc[i, 'Country/Region']
        last_update = df.loc[i, 'Last Update']
        confirmed = df.loc[i, 'Confirmed']
        deaths = df.loc[i, 'Deaths']
        recovered = df.loc[i, 'Recovered']
        latitude = df.loc[i, 'Latitude']
        longitude = df.loc[i, 'Longitude']

        key = (province, country, last_update)
        if key in kvmap:
            confirmed0, deaths0, recovered0, latitude0, longitude0 = kvmap[key]

            # if we have put dummy value previously but got some good value then put that lat lon
            if latitude0 == 200 and longitude0 == 200:
                if pd.isna(latitude) or pd.isna(longitude):
                    kvmap[key] = confirmed0 + confirmed, deaths + deaths0, recovered + recovered0, 200, 200
                else:
                    kvmap[key] = confirmed0 + confirmed, deaths + deaths0, recovered + recovered0, latitude, longitude
            else:
                kvmap[key] = confirmed0 + confirmed, deaths + deaths0, recovered + recovered0, latitude0, longitude0
        else:
            kvmap[(province, country, last_update)] = (confirmed,
                                                       deaths,
                                                       recovered,
                                                       # put dummy value if lat lon not is not available
                                                       200 if pd.isna(latitude) else latitude,
                                                       200 if pd.isna(longitude) else longitude)

    data = []
    for k, v in kvmap.items():
        data.append([key for key in k] + [val for val in v])

    df = pd.DataFrame(data=data,
                      columns=columns)

    df.to_csv(os.path.join(output_dir, '{}.csv'.format(time)), index=False)

    print(len(df), df['Confirmed'].sum())

    write(os.path.join(output_dir, 'config.json'), 'last_updated', time)
    write(os.path.join(output_dir, 'update-date.json'), 'last_updated', time)


time = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')
print("processing", time)
export_csv(
    'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
        time), time, 'data')

"""
# Automatic script to pull multiple data in date range

start = datetime.strptime('06-28-2020', '%m-%d-%Y')
end = datetime.strptime('08-02-2020', '%m-%d-%Y')

# multiple
offset = 0
while start <= end:
    time = datetime.strftime(start + timedelta(offset), '%m-%d-%Y')
    try:
        export_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
                time), time, 'data')
        offset += 1
    except:
        continue
"""