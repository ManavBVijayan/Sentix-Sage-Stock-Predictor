from django.shortcuts import render
from Data.models import News
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob


def analyze_news_data():
    # Download NLTK resources
    nltk.download('wordnet')
    nltk.download('stopwords')

    # Retrieve news data from the database
    news_data = list(News.objects.all().values())
    # Convert news data to a pandas DataFrame
    df = pd.DataFrame(news_data)
    # Perform sentiment analysis and relevance score calculation for each news item
    df['sentiment_score'] = df['headline'].apply(sentiment_analysis)
    df['relevance_score'] = df['headline'].apply(relevance_score)

    return df


def sentiment_analysis(headline):
    blob = TextBlob(headline)
    sentiment = blob.sentiment.polarity
    return sentiment


def relevance_score(headline):
    # Define your keyword dictionaries and weights here
    financial_terms = {
        "earnings report": 2,
        "revenue": 2,
        "growth": 2,
        "profit": 1.5,
        "loss": 1.5,
        "investment": 1,
        "acquisition": 1,
        "merger": 1,
        "market share": 1,
        "debt": 1,
        "cash flow": 1,
        "dividend": 1,
        "recession": 1,
        "inflation": 1,
        "interest rates": 1,
        "currency": 1,
        "commodity": 1,
        "services revenue": 1.2,
        "eps": 1,
        "p/e": 0.75,
        "market cap": 0.75,
        "dividend yield": 0.5,
        "analyst estimates": 1,
        "patent": 1,
    }

    apple_specific = {
        "ios": 0.75,
        "ipad": 0.75,
        "iphone": 0.75,
        "macbook": 0.75,
        "watch": 0.75,
        "airpods": 0.75,
        "siri": 0.75,
        "apple tv+": 0.75,
        "ar/vr": 1,
        "car": 1,
        "chip shortage": 1,
        "supply chain": 1,
        "china": 1,
        "regulation": 1,
    }

    sentiment = {"soar": 0.5, "plummet": 0.5, "bullish": 0.25, "bearish": 0.25}
    sentiment_modifiers = {"very": 1.2, "extremely": 1.5}

    business_context = {
        "competition": 1,
        "industry": 1,
        "outlook": 1,
        "forecast": 1,
        "analyst": 1,
        "upgrade": 1,
        "downgrade": 1,
        "strategy": 1,
        "innovation": 1,
        "market trends": 1,
        "competitor performance": 1,
        "product launches": 1,
        "consumer demand": 1.2,
        "supply chain disruption": 1.2,
        "iphone 14": 1.2,
    }

    product_performance = {
        "iphone sales": 1.5,
        "ipad sales": 1,
        "mac sales": 1,
        "apple watch sales": 1,
        "services revenue": 1.2,
        "app store revenue": 1,
        "itunes revenue": 1,
        "apple tv+ subscriptions": 1,
        "apple music subscriptions": 1,
    }

    technological_advancements = {
        "ios updates": 1,
        "macos updates": 1,
        "hardware upgrades": 1,
        "software innovations": 1,
        "chip design": 1,
        "ar/vr development": 1,
    }

    partnerships_collaborations = {
        "partnership agreements": 1,
        "joint ventures": 1,
        "collaborations with other companies": 1,
        "strategic alliances": 1,
    }

    regulatory_legal_issues = {
        "antitrust investigations": 1,
        "regulatory compliance": 1,
        "patent disputes": 1,
        "privacy concerns": 1,
        "legal settlements": 1,
    }

    market_analysis = {
        "market trends": 1,
        "competitor performance": 1,
        "industry outlook": 1,
        "market forecasts": 1,
        "market share analysis": 1,
    }

    consumer_sentiment = {
        "customer satisfaction": 1,
        "brand loyalty": 1,
        "consumer feedback": 1,
        "social media sentiment": 1,
        "customer complaints": 1,
    }

    global_economic_factors = {
        "global economic indicators": 1,
        "currency exchange rates": 1,
        "trade tensions": 1,
        "geopolitical events": 1,
        "global supply chain disruptions": 1,
    }

    esg_factors = {
        "environmental initiatives": 1,
        "social responsibility efforts": 1,
        "corporate governance practices": 1,
        "sustainability initiatives": 1,
        "diversity and inclusion policies": 1,
    }

    # Merge all keyword dictionaries

    keywords = {**financial_terms, **apple_specific, **sentiment, **sentiment_modifiers, **business_context,
                **product_performance, **technological_advancements, **partnerships_collaborations,
                **regulatory_legal_issues, **market_analysis, **consumer_sentiment, **global_economic_factors,
                **esg_factors}

    weights = {**financial_terms, **apple_specific, **sentiment, **sentiment_modifiers, **business_context,
               **product_performance, **technological_advancements, **partnerships_collaborations,
               **regulatory_legal_issues, **market_analysis, **consumer_sentiment, **global_economic_factors,
               **esg_factors}

    score = 0
    pre_processed_headline = re.sub(r'[^\w\s]', '', headline.lower())
    tokens = pre_processed_headline.split()
    stop_words = stopwords.words('english')
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    processed_headline = " ".join([lemmatizer.lemmatize(word) for word in tokens])

    for keyword, weight in keywords.items():
        occurrences = len(re.findall(rf"\b{keyword}\b", processed_headline))
        score += occurrences * weight

    max_possible_score = sum(weights.values())
    normalized_score = score / max_possible_score if max_possible_score > 0 else 0
    return round(normalized_score, 3)
