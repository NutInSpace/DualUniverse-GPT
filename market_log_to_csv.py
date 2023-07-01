import os
import re
import csv
import sys
import json
import warnings
import requests

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogParser():
    def __init__(sell_orders = True, select_item = "Hematite", enable_watch_dog = False):
        # ARGs / Configuration
        # sell_orders False = use buy_orders instead
        # select_item = what item we want to inspect

        # Step 0: Download items.json
        url = 'https://raw.githubusercontent.com/NutInSpace/DualUniverse-GPT/main/items.json'
        response = requests.get(url)
        items_data = response.json()

        # Step 0: Look Up Item Id
        _select_id = 0 
        for temp in items_data:
            if temp['displayNameWithSize'] == select_item:
                _select_id = temp['id']
                break

        if _select_id == 0:
            sys.exit("Unable to find item in items.json")

        # Step 1: Retrieve log files
        log_directory = os.path.expandvars(r'%localappdata%\NQ\DualUniverse\log')
        log_files = os.listdir(log_directory)
        print(f"Log files:")
        for lf in log_files: print(f"{lf}")

        # Step 2: Parse log files and extract market order data
        def parse_log_file(file_path, sell_orders=True):
            market_order_data = []
            market_buy_order_data = []
            market_sell_order_data = []

            try:
                with open(file_path, 'r', encoding='utf-8') as log_file:
                    log_content = log_file.read()

                    # Use regular expressions to extract the market order information
                    pattern = r'MarketOrder:\[marketId = (\d+), orderId = (\d+), itemType = (\d+), buyQuantity = (.*?), expirationDate = @\(\d+\) (.*?), updateDate = @\(\d+\) (.*?), unitPrice = Currency:\[amount = (\d+)\]'
                    matches = re.findall(pattern, log_content)
                    
                    # For print status
                    e = "                                                                            \r"

                    for match in matches:
                        market_id = int(match[0])
                        order_id = int(match[1])
                        item_type = int(match[2])
                        buy_quantity = int(match[3])
                        expiration_date = match[4]
                        # Don't Care update_date = match[5]
                        unit_price = int(match[6])

                        market_order = {
                            'market_id': market_id,
                            'order_id': order_id,
                            'item_type': item_type,
                            'buy_quantity': buy_quantity,
                            'expiration_date': expiration_date,
                            # Don't Care 'update_date': update_date,
                            'unit_price': unit_price
                        }

                        # Filter items
                        if item_type != _select_id:
                            continue

                        # Save Data
                        if market_order not in market_order_data:
                            market_order_data.append(market_order)
                            # Sell Order
                            if buy_quantity < 0:
                                market_buy_order_data.append(market_order)
                            else:
                                market_sell_order_data.append(market_order)
                        
                        if sell_orders:
                            print(f"Sell Orders Processed = {len(market_sell_order_data)}", end=e)
                        else:
                            print(f"Buy Orders Processed = {len(market_buy_order_data)}", end=e)

            except (PermissionError, UnicodeDecodeError):
                print("Permission Error")
                pass

            if sell_orders:
                return market_sell_order_data
            else:
                return market_buy_order_data

        def process_log_files(sell_orders=True):
            market_orders = []
            for log_file in log_files:
                log_file_path = os.path.join(log_directory, log_file)
                market_orders.extend(parse_log_file(log_file_path, sell_orders))

            # Step 3: Match item information
            def get_item_info(item_id, key='displayNameWithSize'):
                for temp in items_data:
                    if temp['id'] == item_id:
                        return temp[key]
                return None

            def match_item_info(market_orders):
                for order in market_orders:
                    item_id = order['item_type']
                    order['item_name'] = get_item_info(item_id)

            match_item_info(market_orders)

            # Step 4: Write market order data to CSV file
            def write_market_orders_to_csv(market_orders):
                filename = select_item + '_market_orders.csv'
                if sell_orders:
                    filename = "sell_" + filename
                else:
                    filename = "buy_" + filename
                # Now in data folder
                filename = "data\\" + filename

                with open(filename, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=market_orders[0].keys())
                    writer.writeheader()
                    writer.writerows(market_orders)

                print(f"Market orders data written to {filename}")

            write_market_orders_to_csv(market_orders)

            # Step 5: Create animation of real-time price changes
            '''
            def animate_prices(item_name):
                fig, ax = plt.subplots()

                def update(frame):
                    # Retrieve and update the price data for the given item_name
                    # Implement your logic to get the current price for animation
                    price_data = [10.0, 15.0, 12.5, 20.0, 18.0]  # Dummy price data

                    # Clear the plot and set new data
                    ax.clear()
                    ax.plot(price_data)

                ani = animation.FuncAnimation(fig, update, interval=1000)
                plt.show()

            # Call the animation function with the item to track
            animate_prices(item_to_track)
            '''

        # Initial processing of log files
        process_log_files(sell_orders=True)
        process_log_files(sell_orders=False)

        # Disable watchdog for now
        if enable_watch_dog:
            # Watchdog event handler to detect changes in the log directory
            class LogFileEventHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    # process_log_files()
                    process_log_files(sell_orders=False)

            # Set up the watchdog observer
            event_handler = LogFileEventHandler()
            observer = Observer()
            observer.schedule(event_handler, path=log_directory, recursive=False)
            observer.start()

            # Start the event loop for the observer
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                observer.stop()

            observer.join()
