import datetime

import yfinance as yf
from Data.models import StockPrice
import logging

logger = logging.getLogger(__name__)


def collect_stock_data(c_symbol):
    logger.info(f"Collecting data for {c_symbol}")
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    try:
        # download stock data
        data = yf.download(c_symbol, start='2021-12-31', end=today)
        # Select desired columns
        data = data[['Open', 'High', 'Low', 'Close']]
        data.reset_index(inplace=True)
        # Iterate through downloaded data and add/update entries
        for index, row in data.iterrows():
            date = row['Date']
            stock_price, created = StockPrice.objects.get_or_create(
                date=date,
                symbol=c_symbol,
                defaults={
                    'open_price': row['Open'],
                    'high_price': row['High'],
                    'low_price': row['Low'],
                    'close_price': row['Close'],
                }
            )
            if not created:
                # Update existing record with new price data
                stock_price.open_price = row['Open']
                stock_price.high_price = row['High']
                stock_price.low_price = row['Low']
                stock_price.close_price = row['Close']
                stock_price.save()
            else:
                logger.info(f"New entry created for {c_symbol} on {date}")

        logger.info(f"Data collection completed for {c_symbol}")

    except Exception as e:
        logger.error(f"Error collecting data for {c_symbol}: {e}")
