import os
import re
import csv
import sys
import json
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DataProcessor:
    def __init__(self, sell_orders=True, select_item="Hematite", enable_watch_dog=False):
        self._items_data = self._download_items()
        self._select_id = self._get_selected_item_id(select_item)
        self._log_directory = os.path.expandvars(r'%localappdata%\NQ\DualUniverse\log')
        self._log_files = os.listdir(self._log_directory)
        self._process_log_files(sell_orders=sell_orders)
        if enable_watch_dog:
            self._setup_watchdog()

    def _download_items(self):
        url = 'https://raw.githubusercontent.com/NutInSpace/DualUniverse-GPT/main/items.json'
        response = requests.get(url)
        return response.json()

    def _get_selected_item_id(self, select_item):
        for temp in self._items_data:
            if temp['displayNameWithSize'] == select_item:
                return temp['id']
        sys.exit("Unable to find item in items.json")

    def _process_log_files(self, sell_orders=True):
        market_orders = []
        for log_file in self._log_files:
            log_file_path = os.path.join(self._log_directory, log_file)
            market_orders.extend(self._parse_log_file(log_file_path, sell_orders))

        self._match_item_info(market_orders)
        self._write_market_orders_to_csv(market_orders, sell_orders)

    def _parse_log_file(self, file_path, sell_orders=True):
        market_order_data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as log_file:
                market_order_data = self._extract_market_orders(log_file, sell_orders)
        except (PermissionError, UnicodeDecodeError):
            print("Permission Error")
        return market_order_data

    def _extract_market_orders(self, log_file, sell_orders):
        log_content = log_file.read()
        pattern = r'MarketOrder:\[marketId = (\d+), orderId = (\d+), itemType = (\d+), buyQuantity = (.*?), expirationDate = @\(\d+\) (.*?), updateDate = @\(\d+\) (.*?), unitPrice = Currency:\[amount = (\d+)\]'
        matches = re.findall(pattern, log_content)

        market_order_data = []
        e = "                                                                            \r"

        for match in matches:
            item_type = int(match[2])
            if item_type != self._select_id:
                continue

            market_order = {
                'market_id': int(match[0]),
                'order_id': int(match[1]),
                'item_type': item_type,
                'buy_quantity': int(match[3]),
                'expiration_date': match[4],
                'unit_price': int(match[6])
            }

            if market_order not in market_order_data:
                market_order_data.append(market_order)
                print(f"Sell Orders Processed = {len(market_order_data)}", end=e) if sell_orders else print(f"Buy Orders Processed = {len(market_order_data)}", end=e)

        return market_order_data

    def _get_item_info(self, item_id, key='displayNameWithSize'):
        for temp in self._items_data:
            if temp['id'] == item_id:
                return temp[key]
        return None

    def _match_item_info(self, market_orders):
        for order in market_orders:
            item_id = order['item_type']
            order['item_name'] = self._get_item_info(item_id)

    def _write_market_orders_to_csv(self, market_orders, sell_orders):
        prefix = "sell_" if sell_orders else "buy_"
        filename = prefix + '_market_orders.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=market_orders[0].keys())
            writer.writeheader()
            writer.writerows(market_orders)
        print(f"Market orders data written to {filename}")

    def _setup_watchdog(self):
        class LogFileEventHandler(FileSystemEventHandler):
            def on_modified(self, event):
                self._process_log_files(sell_orders=False)

        event_handler = LogFileEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path=self._log_directory, recursive=False)
        observer.start()

        try:
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
