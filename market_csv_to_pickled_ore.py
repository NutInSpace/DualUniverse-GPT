import argparse

import concurrent.futures
import pandas as pd
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
from mplfinance.original_flavor import candlestick_ohlc
from data_processing import LogParser

class DataProcessor:
    def __init__(self, item_name):
        self.item_name = item_name

        # Function to format y axis values
        def currency(x, pos):
            'The two args are the value and tick position'
            return '${:,.2f}'.format(x)

        self.currency_formatter = FuncFormatter(currency)

    def simple_plot(self, buy_orders, sell_orders, num_days=10, bid_min=1, bid_max=1000000, show=True):
        # Convert 'expiration_date' to datetime type, for testing old data apply an offset
        buy_orders['expiration_date'] = pd.to_datetime(buy_orders['expiration_date']) # + pd.DateOffset(days=30)
        sell_orders['expiration_date'] = pd.to_datetime(sell_orders['expiration_date'])

        # First, add a new column 'order_type' to distinguish between buy and sell orders
        buy_orders['order_type'] = 'Buy'
        sell_orders['order_type'] = 'Sell'

        # Combine the two dataframes
        combined = pd.concat([buy_orders, sell_orders])

        # Now we have df
        df = combined

        # Scale for plotting
        df['unit_price'] = df['unit_price'] / 100

        # Filter Stupid Players
        df = df[df['unit_price'] < 250]
        df = df[df['unit_price'] > 1]

        # Filter expired orders
        current_time = pd.Timestamp.now()
        expiration_limit = current_time - pd.DateOffset(days=num_days)
        df = df[df['expiration_date'] > expiration_limit]
        df['expires_in_days'] = df['expiration_date'] - current_time

        # Get the ore tier
        df['ore_tier'] = df['item_name'].map(ore_tiers)

        # Adjust the bid_max based on the ore tier
        df['bid_max'] = df['ore_tier'].map({1: bid_max, 2: bid_max * 2, 3: bid_max * 3})

        # Create a barplot
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=df, x='expires_in_days', y='unit_price', hue='order_type')
        ax.yaxis.set_major_formatter(self.currency_formatter)

        date_format = DateFormatter("%d")
        ax.xaxis.set_major_formatter(date_format)

        # Setting the x-axis format
        plt.xlabel('Days')
        ax.set_ylabel('Unit Price')

        # Adding labels and title
        plt.title(f'All Markets : Unit price of Buy and Sell Orders : {self.item_name}')
        if show:
            plt.show()

        return df

def process_item(item, ParseLogs=True, ShowPlots=True):
    # Parse Log Files
    if ParseLogs:
        LogParser(item_name=item)

    # Setup Visualizer
    data_processor = DataProcessor(item)

    # Read Data
    buy_orders = pd.read_csv(f'data\\csv\\buy_{item}_market_orders.csv')
    sell_orders = pd.read_csv(f'data\\csv\\sell_{item}_market_orders.csv')

    # Get the ore tier
    ore_tier = ore_tiers.get(item, 1)

    # Determine the bid_max based on the ore tier
    _max = 5000
    if ore_tier == 1:
        _max = 250
    elif ore_tier == 2:
        _max = 500
        
    # Razzle Dazzle
    df = data_processor.simple_plot(buy_orders, sell_orders, num_days=10, bid_min=1, bid_max=_max, show=ShowPlots)

    # Pickle the dataframe
    df.to_pickle(f'data\\pickle\\{item}.pickle')


## Main ###
item_names = [
    'Hematite', 'Quartz', 'Coal', 'Bauxite', 
    'Chromite', 'Limestone', 'Malachite',
    'Acanthite', 'Garnierite', 'Petalite', 'Pyrite',
    'Cobaltite', 'Cryolite', 'Gold_nuggets', 'Kolbeckite',
    'Columbite', 'Ilmenite', 'Rhodonite', 'Vanadinite'
]

# Define the ore tiers
ore_tiers = {
    'Hematite': 1, 'Quartz': 1, 'Coal': 1, 'Bauxite': 1,
    'Chromite': 2, 'Limestone': 2, 'Malachite': 2,
    'Acanthite': 3, 'Garnierite': 3, 'Petalite': 3, 'Pyrite': 3,
    'Cobaltite': 4, 'Cryolite': 4, 'Gold_nuggets': 4, 'Kolbeckite': 4,
    'Columbite': 5, 'Ilmenite': 5, 'Rhodonite': 5, 'Vanadinite': 5
}

# Argument parsing
parser = argparse.ArgumentParser(description='Process item data.')
parser.add_argument('--no-parse-logs', dest='parse_logs', action='store_false', help='Do not parse log files')
parser.add_argument('--no-show-plots', dest='show_plots', action='store_false', help='Do not show plots')
parser.set_defaults(parse_logs=True, show_plots=True)
args = parser.parse_args()

# Create a ThreadPoolExecutor
MultiThread = False
if MultiThread:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for each item
        futures = [executor.submit(process_item, item, args.parse_logs, args.show_plots) for item in item_names]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
else:
    for _item in item_names:
        process_item(_item, args.parse_logs, args.show_plots)
