from splinter import Browser
from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import datetime as dt
import time
import re

def scrape_all():
    """Main WebScraping Function"""
    # Initiate chromedriver.
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    # Call mars_news scrape function to collect title and paragraph text.
    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(browser),
        "last_modified": dt.datetime.now()
    }

    
    #stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    """Scrape Mars News"""
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    
    #Get first list item and wait half a second
    browser.is_element_present_by_css ("ul.item_list li.slide", wait_time=0.5)
    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_= "content_title").get_text()
        news_p = slide_elem.find("div", class_= "article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    """Scrape Featured Image"""
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    #Find and click the full image button
    full_image_elem = browser.find_by_id("full_image")
    full_image_elem.click()

    #Find the more info button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_elem = browser.links.find_by_partial_text("more info")
    more_info_elem.click()

    #Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    #Find the relative html url
    img = img_soup.select_one("figure.lede a img")

    try:
        featured_image_url = img.get("src")
    
    except AttributeError:
        return None

    featured_image_url = f"https://www.jpl.nasa.gov{featured_image_url}"

    return featured_image_url


def hemispheres(browser):
    """Scrape hemispheres data"""
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []
    for i in range (4):
         # Find Element on Each Loop to Avoid a Stale Element Exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemi_data)
        # Navigate Backwards
        browser.back()
    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # Soupify the html text
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere


def twitter_weather(browser):
    """Scrape Twitter Weather"""
    # browser = Browser('chrome', headless=False)                             
    url = 'https://twitter.com/marswxreport?lang=en'                      
    browser.visit(url) 
    time.sleep(5)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    # tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    # mars_weather_tweet = weather_soup.find("div", attrs=tweet_attrs)

    # try:
    #     mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()
    # except AttributeError:
    #     pattern = re.compile(r'sol')
    #     mars_weather = weather_soup.find('span', text=pattern).text

    latest_tweets = weather_soup.find_all('span')
    all_tweets = []
    for x in latest_tweets:
        x = x.text
        if len(x) >100:
            all_tweets.append(x)

    for i in all_tweets:
        if "InSight" in i:
            mars_weather = i 
            break 
        else:
            continue

    return mars_weather

def mars_facts(browser):
    """Scrape Mars Facts HTML Table"""
    try:
        df = pd.read_html("https://space-facts.com/mars/")[1]
    except BaseException:
        return None

    df.columns = ['param', 'description', 'value']
    html_table = df.to_html(table_id="html_tbl_css",justify='left',index=False)
    data = df.to_dict(orient='records')  

    # df.column = ["description", "value"]
    # df.set_index("description", inplace=True)
    return df.to_html(classes = 'table table-striped')

if __name__ == "__main__":
    # If running script, print scraped data.
    print(scrape_all())