from matplotlib import pyplot as plt
from spyre import server

import pandas as pd
import urllib.request
import json
import os
import io
from datetime import datetime, timedelta


def download_data():
    ids = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21, 11: 9, 13: 10, 14: 11, 15: 12, 16: 13,
           17: 14, 18: 15, 19: 16, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 26: 7, 27: 5}
    dfs = []
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'Region_ID']

    for i in ids.keys():
        id = ids[i]

        url = 'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1981&year2=2020&type=Mean'.format(
            i)
        wp = urllib.request.urlopen(url)
        text = wp.read()

        text = text.replace(b"<br>", b"")
        text = text.replace(b"<tt><pre>", b"")
        text = text.replace(b"</pre></tt>", b"")

        text = text.decode('utf-8')
        text = io.StringIO(text)

        df = pd.read_csv(text, header=1, names=headers)
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df['Region_ID'] = id
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


if not os.path.isfile("df.csv"):
    df = download_data()
    df.to_csv('df.csv')


def week_to_date(year, week_num):
  first_day_of_year = datetime(int(year), 1, 1)
  date = first_day_of_year + timedelta(days=(week_num - 1) * 7)

  return date


class SimpleApp(server.App):
    title = "NOAA data vizualization"

    region_options = [
        {"label": "Vinnytsia", "value": "1"},
        {"label": "Volyn", "value": "2"},
        {"label": "Dnipropetrovsk", "value": "3"},
        {"label": "Donetsk", "value": "4"},
        {"label": "Zhytomyr", "value": "5"},
        {"label": "Zakarpattia", "value": "6"},
        {"label": "Zaporizhzhia", "value": "7"},
        {"label": "Ivano-Frankivsk", "value": "8"},
        {"label": "Kyiv", "value": "9"},
        {"label": "Kirovohrad", "value": "10"},
        {"label": "Luhansk", "value": "11"},
        {"label": "Lviv", "value": "12"},
        {"label": "Mykolaiv", "value": "13"},
        {"label": "Odessa", "value": "14"},
        {"label": "Poltava", "value": "15"},
        {"label": "Rivne", "value": "16"},
        {"label": "Sumy", "value": "17"},
        {"label": "Ternopil", "value": "18"},
        {"label": "Kharkiv", "value": "19"},
        {"label": "Kherson", "value": "20"},
        {"label": "Khmelnytskyi", "value": "21"},
        {"label": "Cherkasy", "value": "22"},
        {"label": "Chernivtsi", "value": "23"},
        {"label": "Chernihiv", "value": "24"},
        {"label": "Crimea", "value": "25"}
    ]

    inputs = [
        {
            "type": 'dropdown',
            "label": 'NOAA data dropdown',
            "options": [{"label": "VCI", "value": "VCI"},
                        {"label": "TCI", "value": "TCI"},
                        {"label": "VHI", "value": "VHI"}],
            "key": 'ticker',
            "action_id": 'update_data'
        },
        {
            "type": 'dropdown',
            "label": 'Region',
            "options": region_options,
            "key": 'region',
            "action_id": 'update_data'
        },
        {
            "type": 'text',
            "label": 'Range of years',
            "key": 'years',
            "value": '2005-2010',
            "action_id": 'update_data'
        },
        {
            "type": 'text',
            "label": 'Range of weeks',
            "key": 'weeks',
            "value": '9-35',
            "action_id": 'update_data'
        }
    ]

    controls = [{"type": "hidden", "id": "update_data"}]

    tabs = ["Plot", "Table"]

    outputs = [
        {
            "type": 'plot',
            "id": 'plot',
            "control_id": 'update_data',
            "tab": 'Plot',
            "on_range_load": True
        },
        {
            "type": 'table',
            "id": 'table',
            "control_id": 'update_data',
            "tab": 'Table',
            "on_page_load": True
        }
    ]

    def getData(self, params):
        df = pd.read_csv("df.csv")
        ticker = params['ticker']
        region = int(params['region'])

        years = params['years'].split('-')
        if len(years) == 2:
            start_year = int(years[0])
            end_year = int(years[1])
        elif len(years) == 1:
            if years[0]:
                start_year = end_year = int(years[0])
            else:
                start_year = end_year = 1982
        else:
            start_year = end_year = 1982

        weeks = params['weeks'].split('-')
        if start_year == end_year:
            if len(weeks) == 2:
                start_week = int(weeks[0])
                end_week = int(weeks[1])
            elif len(weeks) == 1:
                if weeks[0]:
                    start_week = end_week = int(weeks[0])
                else:
                    start_week, end_week = 1, 52
            else:
                start_week, end_week = 1, 52
        else:
            start_week, end_week = 1, 52

        if start_year > end_year:
            start_year, end_year = end_year, start_year
        if start_week >= end_week:
            start_week, end_week = end_week, start_week

        data = df[(df['Region_ID'] == region) & (df['Year'] >= start_year) & (df['Year'] <= end_year) & (df['Week'] >= start_week) & (df['Week'] <= end_week)]
        data.loc[:, 'Date'] = data.apply(lambda row: week_to_date(row['Year'], row['Week']), axis=1)
        data = data[['Date', 'Year', 'Week', ticker, 'Region_ID']]

        return data

    def getPlot(self, params):
        df = self.getData(params).set_index('Date')
        ticker = params['ticker']
        region = next((item["label"] for item in self.region_options if item["value"] == params['region']), None)

        plt_obj = df.plot(y=ticker, figsize=(24, 10), marker='o', markersize=5)
        plt_obj.set_ylabel(ticker)
        plt_obj.set_title(f'{ticker} in {region}')

        fig = plt_obj.get_figure()
        return fig

app = SimpleApp()
app.launch(port=9094)
