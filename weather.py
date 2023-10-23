"""
This script gets weather forecast data for current day and for specified place (24 hours).
It uses public <weatherapi.com> api.
It can save the data into csv file and plot it using matplotlib and pandas libraries.
"""
import logging
import os
import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import requests
import click

KEY = os.environ["KEY"]
URL = "https://api.weatherapi.com/v1/forecast.json?key={KEY}&q={PLACE}&days=1&aqi=no&alerts=no"

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


class CSVWeather:
    def __init__(self, file_name: str = "default.csv", folder_name: str = "data"):
        """Constructor for CSVWeather class
        :param file_name: csv file name, where forecast data will be saved
        :param folder_name: the directory where csv file will be created/readed
        """
        self.file_name = file_name
        self.folder_name = folder_name
        self.path = pathlib.Path(self.folder_name)
        self.name = None
        self.current_temp = None
        self.last_updated = None
        self.forecast = None
        self.current_date_time_temp = None
        self.localtime = None

    def get_data(self, place):
        """This function gets the data from API using HTTP GET method"""
        resp = requests.get(URL.format(KEY=KEY, PLACE=place))
        dct_resp = resp.json()
        resp.raise_for_status()
        self.name = dct_resp["location"]["name"]
        self.localtime = dct_resp["location"]["localtime"]
        self.current_temp = float(dct_resp["current"]["temp_c"])
        self.last_updated = dct_resp["current"]["last_updated"]
        self.forecast = dct_resp["forecast"]["forecastday"][0]["hour"]
        self.current_date_time_temp = (
            f"{self.name}: {self.last_updated}: {self.current_temp} C"
        )

    def write_csv(self):
        """This function writes forecast data into the csv file"""
        self.path.mkdir(exist_ok=True)
        f = open(self.path.joinpath(self.file_name), "w")
        f.write("date,time,temp_c,place\n")
        for i in self.forecast:
            date_time = i["time"]
            date, time = date_time.split()
            temp_c = i["temp_c"]
            c = f"{date},{time},{temp_c},{self.name}\n"
            f.write(c)

            logger.debug(c)
        logger.debug("CSV file created")

    def plot(self):
        """This function reads the data from csv file and plots it."""
        df = pd.read_csv(self.path.joinpath(self.file_name))
        df["temp_c"].apply(pd.to_numeric)
        logger.debug(df)
        df.plot(
            x="time",
            y="temp_c",
            linewidth=2.5,
            color="green",
            marker="^",
            linestyle="solid",
        )
        plt.xlabel(
            "Time [h]",
        )
        plt.ylabel("temperature [C]")
        date = df["date"][0]
        place = df["place"][0]
        plt.title(place + " " + date)
        plt.yticks(fontsize=10)
        plt.show()


@click.command()
@click.option('--update_place', default=None, help='Download and save data for given place')
@click.option('--plot', is_flag=True, help='Plot the graph')
def main(update_place, plot):
    ob = CSVWeather()
    if update_place:
        ob.get_data(update_place)
        ob.write_csv()
    if plot:
        ob.plot()
    if not plot and not update_place:
        with click.Context(main) as ctx:
            click.echo(main.get_help(ctx))


if __name__ == "__main__":
    main()
