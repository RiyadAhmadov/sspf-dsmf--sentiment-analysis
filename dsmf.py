from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd

# Initialize WebDriver (make sure you have the ChromeDriver installed)
driver_path = r'C:\Users\HP\OneDrive\İş masası\More\chromedriver-win64\chromedriver-win64\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Navigate to Instagram login page
url = "https://www.instagram.com/accounts/login/"
driver.get(url)
time.sleep(3)

# Login (Replace with your username and password)
username = driver.find_element(By.NAME, "username")
password = driver.find_element(By.NAME, "password")
username.send_keys("about_1tech")
time.sleep(5)
password.send_keys("eriya4949494949")
time.sleep(5)
password.send_keys(Keys.RETURN)
time.sleep(5)

# Go to the target Instagram page
page_url = "https://www.instagram.com/dsmf.sosial.gov.az/"
driver.get(page_url)
time.sleep(5)

# Scroll down to load more posts (limit to 2 scrolls)
SCROLL_PAUSE_TIME = 2
scroll_attempts = 300

for _ in range(scroll_attempts):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

# Collect post URLs
post_links = []
soup = BeautifulSoup(driver.page_source, 'html.parser')
for a in soup.find_all('a', href=True):
    if '/p/' in a['href']:
        post_links.append("https://www.instagram.com" + a['href'])
        print(a['href'])
    if len(post_links) >= 2000:  # Stop after collecting 2 posts
        break

def scrape_comments(post_url):
    driver.get(post_url)
    time.sleep(2)

    # Load all comments
    while True:
        try:
            load_more_comments = driver.find_element(By.XPATH, '//button[contains(text(), "Load more comments")]')
            load_more_comments.click()
            time.sleep(2)
        except:
            break

    # Parse comments
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all span elements with the specified class attributes
    comments = soup.find_all('span', class_="x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj")

    time_tag = soup.find('time', class_="x1p4m5qa")
    datetime_str = time_tag['datetime']
    date_part, time_part = datetime_str.split('T')
    time_part = time_part.split('.')[0]

    post_comments = []
    for comment in comments:
        post_comments.append(comment.text)
    
    post_comments.append(date_part)
    post_comments.append(time_part)
    
    return post_comments

# Scrape comments from the first 2 posts
all_comments = {}
for post_link in post_links:
    print(f"Scraping comments from {post_link}...")
    comments = scrape_comments(post_link)
    # times = scrape_comments(post_link)[1]
    all_comments[post_link] = comments

# Close the driver
driver.quit()

import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.DataFrame(columns=['comment','like_sayı','post_content','user','tarix','zaman'])


# Print or save the scraped comments
for post, comments in all_comments.items():
    print(f"\nPost: {post}")

    df1 = pd.DataFrame(columns=['comment','like_sayı','post_content','user','tarix','zaman'])

    user = comments[1:-3:2]
    comment = comments[2:-3:2]
    like_sayi = comments[-3]
    tarix = comments[-2]
    zaman = comments[-1]
    post_content = comments[0]

    max_len = max(len(user), len(comment))
    user.extend([None] * (max_len - len(user)))
    comment.extend([None] * (max_len - len(comment)))

    df1['user'] = user
    df1['comment'] = comment
    df1['like_sayı'] = like_sayi
    df1['post_content'] = post_content
    df1['tarix'] = tarix
    df1['zaman'] = zaman

    df = pd.concat([df,df1])


df.to_excel(r'C:\Users\HP\OneDrive\İş masası\sd.xlsx', index = False)
    