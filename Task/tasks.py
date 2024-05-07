from celery import shared_task
from Data.stock_data import collect_stock_data
from Data.news_data import bs_news_setup, toi_news_setup, remove_duplicates, save_new_data
from DataPrep_ModelTrain.merge_stock_news_data import merge_data
from DataPrep_ModelTrain.model_training import train_model
from DataPrep_ModelTrain.prediction import prediction
import logging
from AdminDashBoard.models import ProcessLog
from datetime import datetime

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def collect_daily_data(self):
    try:
        # Create or update ProcessLog for the current date
        today = datetime.today().date()  # Get today's date
        process_log, created = ProcessLog.objects.get_or_create(date=today, defaults={'stock_status': False, 'bs_status': False, 'toi_status': False})

        # Log the start of the task
        if created:
            logger.info(f'Starting daily data collection for {today}')

        # Collect stock data
        collect_stock_data('AAPL')

        # Update ProcessLog for stock data collection
        process_log.stock_status = True
        process_log.save()
        logger.info('Stock data collection completed successfully')

        # Call news scraping functions and save data into the database
        news_data = []
        bs_news_setup(news_data)
        toi_news_setup(news_data)
        remove_duplicates(news_data)
        save_new_data(news_data)

        # Update ProcessLog for news data collection
        process_log.bs_status = True
        process_log.toi_status = True
        process_log.save()
        logger.info('News data collection completed successfully')

    except Exception as e:
        logger.error(f"An error occurred during daily data collection: {e}")


@shared_task(bind=True)
def feature_engineering_and_model_training(self):
    try:
        # Get the ProcessLog for the current date (created in collect_daily_data)
        today = datetime.today().date()
        process_log = ProcessLog.objects.get(date=today)

        # Update ProcessLog for model training status
        process_log.model_training_status = False
        process_log.save()

        # Execute data processing and training logic
        data = merge_data()
        mse, r2, next_five_days_close_prices, scaler = train_model(data)
        process_log.model_training_status = True
        process_log.mse = mse
        process_log.r2_score = r2

        # Make predictions and update the corresponding fields
        predicted_values = prediction(next_five_days_close_prices, scaler)
        process_log.day1 = predicted_values[0]
        process_log.day2 = predicted_values[1]
        process_log.day3 = predicted_values[2]
        process_log.day4 = predicted_values[3]
        process_log.day5 = predicted_values[4]
        process_log.save()

        logger.info('Feature engineering and model training task completed successfully')

    except Exception as e:
        logger.error(f"An error occurred during feature engineering and model training: {e}")