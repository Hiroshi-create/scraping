from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes import ReviewContainer
from functions import parse_review_info, reviews_to_csv, get_unique_salon_names

reviews = []

unique_salon_names = get_unique_salon_names('reviews.csv')
print(f"{unique_salon_names}, {len(unique_salon_names)}")

# WebDriverのパスを指定
driver_path = '/usr/local/bin/chromedriver'

# Serviceオブジェクトを作成
service = Service(executable_path=driver_path)

# WebDriverのインスタンスを作成
driver = webdriver.Chrome(service=service)

# URLを指定
url = 'https://beauty.hotpepper.jp/'

# 指定されたURLにアクセス
driver.get(url)

# <area>タグのshapeが"rect"であるタグを取得
areas = driver.find_elements(By.XPATH, "//area[@shape='rect']")
# 各URLに順番に遷移して戻る処理
for i in range(len(areas)):
    area = driver.find_elements(By.XPATH, "//area[@shape='rect']")[i]
    region = area.get_attribute('alt')    # 地方を取得
    print(region)
    href = area.get_attribute('href')
    if href:
        driver.get(href)
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # エリア
        links = driver.find_elements(By.XPATH, "//ul[@class='routeMa']/li/a")
        for j in range(len(links)):
            link = driver.find_elements(By.XPATH, "//ul[@class='routeMa']/li/a")[j]
            prefectures = link.get_attribute('title')    # 都道府県を取得
            print(prefectures)
            sub_href = link.get_attribute('href')
            if sub_href:
                modified_href = sub_href.rstrip('/') + '/salon/'    # その地域のすべてを取得用
                driver.get(modified_href)
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                salonPageNum = 1
                # サロンを順に
                while True:
                    salons = driver.find_elements(By.XPATH, "//ul[@class='slnCassetteList mT20']/li")
                    for p in range(len(salons)):
                        salon = driver.find_elements(By.XPATH, "//ul[@class='slnCassetteList mT20']/li")[p]
                        try:
                            a_tag = salon.find_element(By.XPATH, "./div[2]/div/div[1]/dl[2]/dd[@class='message']/a")
                        except Exception as e:
                            print(f"サロンに口コミがありませんでした: {e}")
                            continue
                        salon_href = a_tag.get_attribute('href')
                        # サロンページへ遷移
                        driver.get(salon_href)
                        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        # サロン情報を取得
                        xpath1 = '//*[@id="mainContents"]/div[1]/div/div[3]/div/p[1]/a'
                        element1 = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath1)))
                        salon_name = element1.text
                        print(salon_name)
                        if salon_name in unique_salon_names:
                            print("取得済みのサロンとコンフリクトしました")
                            driver.back()
                            continue
                        xpath2 = '//*[@id="mainContents"]/div[1]/div/div[3]/div/div/ul/li[1]'
                        element2 = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath2)))
                        salon_adress = element2.text
                        # 口コミ取得
                        reviewPageNum = 1
                        while True:    # ページ
                            reviews_block = driver.find_elements(By.XPATH, "//li[@class='reportCassette mT30']")
                            for r in range(len(reviews_block)):
                                review_block = driver.find_elements(By.XPATH, "//li[@class='reportCassette mT30']")[r]
                                review_info = review_block.find_element(By.XPATH, "./div[1]/div/p/span[2]").text
                                review_text = review_block.find_element(By.XPATH, "./div[2]/p").text
                                text1, text2, text3 = parse_review_info(review_info)
                                reviews.append(ReviewContainer(region, prefectures, salon_name, salon_adress, text1, text2, text3, review_text))
                            # レビュー画面の「次へ」をクリック
                            try:
                                next_review_page = driver.find_element(By.XPATH, "//li[@class='pa top0 right0 afterPage']")
                                next_review_page.click()
                                reviewPageNum += 1
                            except Exception as e:
                                print(f"レビュー画面の「次へ」がなくなった場合? : {e}")
                                # レビュー画面の「次へ」がなくなった場合
                                break
                        for rpb in range(reviewPageNum):
                            driver.back()
                        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        reviews_to_csv(reviews)
                        reviews = []

                    # サロン画面の「次へ」をクリック
                    try:
                        next_page = driver.find_element(By.XPATH, "//a[@class='iS arrowPagingR']")
                        next_page.click()
                        salonPageNum += 1
                    except Exception as e:
                        print(f"サロン画面の「次へ」がなくなった場合? : {e}")
                        # サロン画面の「次へ」がなくなった場合
                        break
                for spb in range(salonPageNum):
                    driver.back()
        
        # <ul class="routeMa">タグの下の<li>タグがなくなればもう一つ遷移を戻る
        if not driver.find_elements(By.XPATH, "//ul[@class='routeMa']/li"):
            driver.back()
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        driver.back()
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# ブラウザを閉じる
driver.quit()