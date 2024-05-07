from Data.models import StockPrice
import pandas as pd
from .senitment_analysis import analyze_news_data


def merge_data():
    data = analyze_news_data()

    average_scores = data.groupby('date')[['sentiment_score', 'relevance_score']].mean().reset_index()

    stock_data = StockPrice.objects.all().values()

    stockprice = pd.DataFrame(stock_data)

    merged_data = pd.merge(average_scores, stockprice, on='date')
    merged_data.sort_values(by='date', inplace=True)
    # merged_data.to_csv('merged_data.csv', index=False)

    return merged_data