import argparse

import concurrent.futures
import pandas as pd
import seaborn as sns

from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
from mplfinance.original_flavor import candlestick_ohlc
from data_processing import LogParser # Rename to market_log_to_csv.py to data_processing.py
from item_helper import ItemManager

class DataProcessor:
    def __init__(self, item_name):
        self.item_name = item_name

        # Function to format y axis values
        def currency(x, pos):
            'The two args are the value and tick position'
            return '${:,.2f}'.format(x)

        self.currency_formatter = FuncFormatter(currency)

        # Item Details
        self.item_manager = ItemManager()

    def process_data(self, buy_orders, sell_orders, num_days=30, bid_min=1, bid_max=2500):
        # Convert 'expiration_date' to datetime type, for testing old data apply an offset
        buy_orders['expiration_date'] = pd.to_datetime(buy_orders['expiration_date']) # + pd.DateOffset(days=30)
        sell_orders['expiration_date'] = pd.to_datetime(sell_orders['expiration_date'])

        # First, add a new column 'order_type' to distinguish between buy and sell orders
        buy_orders['order_type'] = 'Buy'
        buy_orders['buy_quantity'] = abs(buy_orders['buy_quantity'])
        sell_orders['order_type'] = 'Sell'
        sell_orders['buy_quantity'] = abs(sell_orders['buy_quantity'])

        # Combine the two dataframes
        combined = pd.concat([buy_orders, sell_orders])

        # Now we have df
        self.df = combined

        # Scale for plotting
        self.df['unit_price'] = self.df['unit_price'] / 100

        # Filter Stupid Players
        self.df = self.df[self.df['unit_price'] < bid_max]
        self.df = self.df[self.df['unit_price'] > bid_min]

        # Filter expired orders
        current_time = pd.Timestamp.now()
        expiration_limit = current_time - pd.DateOffset(days=num_days)
        self.df = self.df[self.df['expiration_date'] > expiration_limit]
        self.df['expires_in_days'] = self.df['expiration_date'] - current_time

        # Get the ore tier
        self.df['ore_tier'] = self.df['item_name'].map(ore_tiers)

        # Adjust the bid_max based on the ore tier
        self.df['bid_max'] = self.df['ore_tier'].map({1: bid_max, 2: bid_max * 2, 3: bid_max * 3})

        return self.df

    def mean_buy_price(self):
        return self.df[(self.df['order_type'] == 'Buy')]['unit_price'].mean()
    
    def mean_sell_price(self):
        return self.df[(self.df['order_type'] == 'Sell')]['unit_price'].mean()

    def highest_buy_order(self):
        return self.df[(self.df['order_type'] == 'Buy')]['unit_price'].max()
    
    def lowest_sell_order(self):
        return self.df[(self.df['order_type'] == 'Sell')]['unit_price'].min()

    def mean_market_price(self):
        return self.df['unit_price'].mean()

    def calculate_market_mass(self, order_type):
        #market_id_counts = self.df[self.df['order_type'] == order_type]['market_id'].value_counts()
        #if not market_id_counts.empty:
        #    most_common_market = market_id_counts.idxmax()
            # total_value = self.df[(self.df['order_type'] == order_type) & (self.df['market_id'] == most_common_market)]['buy_quantity'].sum()
        #    return total_value
        #else:
        #    return 0
        
        item_mass = self.item_manager.lookup_item_mass(self.item_name)
        return self.df[(self.df['order_type'] == order_type)]['buy_quantity'].sum() * item_mass


    def calculate_market_value(self, order_type):
        #market_id_counts = self.df[self.df['order_type'] == order_type]['market_id'].value_counts()
        #if not market_id_counts.empty:
        #    most_common_market = market_id_counts.idxmax()
            # total_value = self.df[(self.df['order_type'] == order_type) & (self.df['market_id'] == most_common_market)]['buy_quantity'].sum()
        #    return total_value
        #else:
        #    return 0
        return self.df[(self.df['order_type'] == order_type)]['buy_quantity'].sum() * self.mean_market_price()

    def plot_data(self, show=True):
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=self.df, x='buy_quantity', y='unit_price', hue='order_type')
        ax.yaxis.set_major_formatter(self.currency_formatter)

        # Set x-axis to logarithmic scale
        # sns.set_style("whitegrid")
        # plt.xscale("log")

        # Setting the x-axis format
        plt.xlabel('Volume')
        ax.set_ylabel('Unit Price')

        # Set the Grid
        ax.grid = True

        # Limiting the number of x-axis labels
        x = self.df['buy_quantity']
        max_labels = 10  # Maximum number of labels to show
        label_indices = range(0, len(x), len(x)//max_labels)
        plt.xticks(label_indices)

        # Calculate and display total value for each order typef
        buy_value = self.calculate_market_value('Buy')
        sell_value = self.calculate_market_value('Sell')
        sell_mass = self.calculate_market_mass('Sell')
        buy_value /= 1000 # hundred-thousand
        buy_value /= 1000 # millions
        #buy_value /= 1000 # billions
        sell_value /= 1000 # thousand
        sell_value /= 1000 # million
        #sell_value /= 1000 # billion
        sell_mass /= 1000 # K
        sell_mass /= 1000 # Meta
        #sell_mass /= 1000 # Giga

        # Maths
        ## Summary
        plt.text(0.75, 0.45, f'Lowest Sell Order: ${self.lowest_sell_order():,.2f}', transform=ax.transAxes, fontsize=12, fontweight='bold')
        plt.text(0.75, 0.50, f'Highest Buy Order: ${self.highest_buy_order():,.2f}', transform=ax.transAxes, fontsize=12, fontweight='bold')
        
        plt.text(0.75, 0.35, f'Mean Buy Price ${self.mean_buy_price():,.2f}', transform=ax.transAxes, fontsize=10)
        plt.text(0.75, 0.30, f'Mean Sell Price : ${self.mean_sell_price():,.2f}', transform=ax.transAxes, fontsize=10)
        plt.text(0.75, 0.25, f'Mean Price (All) ${self.mean_market_price():,.2f}', transform=ax.transAxes, fontsize=10) 
        plt.text(0.75, 0.20, f'Total Value (Buy): ${buy_value:,.2f}', transform=ax.transAxes, fontsize=10)
        plt.text(0.75, 0.15, f'Total Value (Sell): ${sell_value:,.2f}', transform=ax.transAxes, fontsize=10)
        plt.text(0.75, 0.10, f'Total Mass (Sell): {sell_mass:,.4f} tons', transform=ax.transAxes, fontsize=10)
        plt.text(0.75, 0.05, f'Units in (Billions, Megatons)', transform=ax.transAxes, fontsize=10)

        # Adding labels and title
        today = datetime.today().strftime("%Y-%m-%d")
        num_data_points = len(self.df)
        plt.title(f'All Markets : Unit price of Buy and Sell Orders : {self.item_name}\nDate of Analysis: {today} Sample Pop : {num_data_points}')
        
        if show:
            plt.show()

def process_item(item, ParseLogs=True, ShowPlots=True, Pickle=False):
    # Parse Log Files
    if ParseLogs:
        LogParser(item_name=item)

    # Setup Visualizer
    data_processor = DataProcessor(item)

    # Read Data
    temp_name = item.replace(" ", "_")
    buy_orders = pd.read_csv(f'data\\csv\\buy_{temp_name}_market_orders.csv')
    sell_orders = pd.read_csv(f'data\\csv\\sell_{temp_name}_market_orders.csv')

    # Get the ore tier
    ore_tier = ore_tiers.get(item, 1)

    # Determine the bid_max based on the ore tier
    _max = 5000
    if ore_tier == 1:
        _max = 250
    elif ore_tier == 2:
        _max = 500
    
    df = data_processor.process_data(buy_orders, sell_orders, num_days=10, bid_min=1, bid_max=_max)

    # Razzle Dazzle
    if ShowPlots:
        data_processor.plot_data()

    # Pickle the dataframe
    if Pickle:
        temp_name = item.replace(" ", "_")
        df.to_pickle(f'data\\pickle\\{temp_name}.pickle')


## Main ###
item_names = [
    'Columbite', 'Ilmenite', 'Rhodonite', 'Vanadinite',
    'Cobaltite', 'Cryolite', 'Gold nuggets', 'Kolbeckite',
    'Acanthite', 'Garnierite', 'Petalite', 'Pyrite',
    'Chromite', 'Limestone', 'Malachite',
    'Hematite', 'Quartz', 'Coal', 'Bauxite'
]

# Define the ore tiers
ore_tiers = {
    'Hematite': 1, 'Quartz': 1, 'Coal': 1, 'Bauxite': 1,
    'Chromite': 2, 'Limestone': 2, 'Malachite': 2,
    'Acanthite': 3, 'Garnierite': 3, 'Petalite': 3, 'Pyrite': 3,
    'Cobaltite': 4, 'Cryolite': 4, 'Gold Nuggets': 4, 'Kolbeckite': 4,
    'Columbite': 5, 'Ilmenite': 5, 'Rhodonite': 5, 'Vanadinite': 5
}

# Argument parsing
parser = argparse.ArgumentParser(description='Process item data.')
parser.add_argument('--no-parse-logs', dest='parse_logs', action='store_false', help='Do not parse log files')
parser.add_argument('--no-show-plots', dest='show_plots', action='store_false', help='Do not show plots')
parser.set_defaults(parse_logs=False, show_plots=True)
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
