from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from .models import News


def bs_news_setup(news_data):
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-insecure-permissive-cookies")
    user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0.6367.63 Safari/537.36')
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get('https://www.business-standard.com/search?q=apple')
        print("Page title:", driver.title)

        # Scrape news data
        news_data.append(scrape_business_standard(driver))
        print("Scraped news data:BS")
    except Exception as e:
        print("An error occurred during scraping:", e)

    finally:
        driver.quit()


def scrape_business_standard(driver):
    print('Data collecting is started.....')
    news_data = []
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="panel:R1ap6:0"]')))
    load_more_attempts = 0
    # Load more news until all are loaded
    while True:
        cardlist = element.find_elements(By.CLASS_NAME, 'cardlist')
        try:
            # Retry loop for clicking the "Load More" button
            for _ in range(3):  # Retry 3 times
                try:
                    load_more_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'Loadmore_loadmorebtn__IVsn_')))
                    load_more_btn.click()
                    break  # Break out of the retry loop if click succeeds
                except TimeoutException:
                    print("Timeout occurred while waiting for the element to be clickable. Retrying...")
                    time.sleep(2)

            load_more_attempts += 1
            if load_more_attempts >= 3:
                print("Reached maximum number of load more attempts.")
                break
            time.sleep(2)
        except NoSuchElementException:
            print("Load More button not found, assuming reached end.")
            break

            # Iterate through news elements and extract data
    for news in cardlist:
        headline = news.find_element(By.CLASS_NAME, 'smallcard-title').text.strip()
        updated_date = news.find_element(By.CLASS_NAME, 'MetaPost_metainfo__MmNP0').text.strip()
        date_text_parts = updated_date.split("Last Updated: ")
        date_text = date_text_parts[1].split(" | ")[0]
        date_object = datetime.strptime(date_text, "%b %d %Y")
        date_of_published = date_object.strftime("%Y-%m-%d")
        news_provider = "Business Standard"  # Assuming all news are from Business Standard
        news_item = {
            'date': date_of_published,
            'headline': headline,
            'website': news_provider
        }
        news_data.append(news_item)

    return news_data


def toi_news_setup(news_data):
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-insecure-permissive-cookies")
    user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0.6367.63 Safari/537.36')
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get('https://timesofindia.indiatimes.com/topic/Apple/news?dateFilter=1640889000000,1711909799000')
        print("Page title:", driver.title)

        # Scrape news data
        news_data.append(scrape_toi(driver))

        print("Scraped news data:TOI")

    except Exception as e:
        print("An error occurred during scraping:", e)

    finally:
        driver.quit()


def extract_data_toi(news):
    headline = news.find_element(By.CLASS_NAME, 'fHv_i')
    news_headline = headline.text.strip()

    updated_date = news.find_element(By.CLASS_NAME, 'ZxBIG')
    date_text = updated_date.text.strip()
    date_text = date_text.split(" / ")[-1]
    date_text = date_text.replace(' (IST)', '')
    date_object = datetime.strptime(date_text, "%b %d, %Y, %H:%M")
    date_of_published = date_object.strftime("%Y-%m-%d")

    news_item = {
        'date': date_of_published,
        'headline': news_headline,
        'website': 'TOI'
    }
    return news_item


def scrape_toi(driver):
    news_data = []
    i = 0
    while True:
        try:
            newsbox = driver.find_elements(By.CLASS_NAME, 'uwU81')
            load_more_btn = driver.find_element(By.CLASS_NAME, 'IVNry ')
            i += 1
            if load_more_btn:
                actions = ActionChains(driver)
                actions.move_to_element(load_more_btn).click().perform()
                if i >=1:  # Limit the number of "Load More" clicks
                    print("Reached maximum number of load more attempts.")
                    break
                time.sleep(2)
        except NoSuchElementException:
            print("Load More button not found, assuming reached end.")
            break
        except StaleElementReferenceException:
            print("Stale Element Reference Exception occurred, refreshing elements...")
            continue

    for news in newsbox:
        news_data.append(extract_data_toi(news))

    return news_data


def remove_duplicates(news_data):
    # Convert news_data into a DataFrame
    merged_data = pd.DataFrame([item for sublist in news_data for item in sublist])

    # Sort DataFrame by date and convert headline to lowercase
    merged_data.sort_values(by='date', inplace=True)
    merged_data['headline_processed'] = merged_data['headline'].str.lower()
    vectorizer = TfidfVectorizer(stop_words='english')

    deduplicated_indices = []

    for date in merged_data['date'].unique():
        subset = merged_data[merged_data['date'] == date]

        tfidf_matrix = vectorizer.fit_transform(subset['headline_processed'])

        cosine_sim = cosine_similarity(tfidf_matrix)

        subset_deduplicated_indices = []
        threshold = 0.9

        for i in range(len(cosine_sim)):
            if i not in subset_deduplicated_indices:
                subset_deduplicated_indices.append(i)
                for j in range(i + 1, len(cosine_sim[i])):
                    if cosine_sim[i][j] > threshold:
                        subset_deduplicated_indices.append(j)

        deduplicated_indices.extend(subset.index[subset_deduplicated_indices])
    merged_news_final = merged_data.drop_duplicates(subset=subset.columns, keep=False)

    print('Successfully removed similar news:')
    return merged_news_final


def save_new_data(news_data):
    yesterday = datetime.now().date() - timedelta(days=1)
    most_recent_news = News.objects.order_by('-date').first()

    if most_recent_news:
        most_recent_date = most_recent_news.date
    else:
        most_recent_date = yesterday

    filtered_news_data = []

    for nested_news_list in news_data:
        for news in nested_news_list:
            try:
                date_str = news['date']
                date = datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert string to datetime.date
                if most_recent_date < date < yesterday:  # Compare datetime.date objects
                    filtered_news_data.append(news)
            except KeyError:
                print("Missing key in news data:", news)
            except ValueError as e:
                print("Error converting date:", e)

    for news in filtered_news_data:
        try:
            News.objects.create(
                date=news['date'],
                headline=news['headline'],
                website=news['website']
            )
            print('News added:')
        except Exception as e:
            print("Error saving news data:", e)



# import csv
#
# def export_news_to_csv(file_path):
#     # Open the file in 'write' mode with encoding='utf-8'
#     with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
#         # Create a CSV writer object
#         writer = csv.writer(csvfile)
#
#         # Write CSV header
#         writer.writerow(['Date', 'Headline', 'Website'])
#
#         # Fetch all News objects ordered by date
#         news_objects = News.objects.order_by('date')
#
#         # Write each news object to the CSV file
#         for news in news_objects:
#             writer.writerow([news.date, news.headline, news.website])

