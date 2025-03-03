import csv
import pandas as pd
import os

def parse_review_info(review_info):
    # 初期値をNoneに設定
    text1, text2, text3 = None, None, None
    
    # "（"と"）"を取り除く
    review_info = review_info.strip("（）")
    
    # "/"で分割
    parts = review_info.split("/")
    
    # 各部分を対応する変数に代入
    if len(parts) > 0:
        text1 = parts[0]
    if len(parts) > 1:
        text2 = parts[1]
    if len(parts) > 2:
        text3 = parts[2]
    
    return text1, text2, text3


def reviews_to_csv(reviews, filename="reviews.csv"):
    # データを辞書形式に変換  region, area
    data = {
        "region": [review.region for review in reviews],
        "prefectures": [review.prefectures for review in reviews],
        "salonName": [review.salonName for review in reviews],
        "salonAddress": [review.salonAddress for review in reviews],
        "gender": [review.gender for review in reviews],
        "age": [review.age for review in reviews],
        "profession": [review.profession for review in reviews],
        "review": [review.review for review in reviews]
    }

    # データフレームを作成
    df = pd.DataFrame(data)

    # CSVファイルが存在する場合は追記モードで開く
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

    print(f"データを{filename}に出力しました。")

def get_unique_salon_names(file_path):
    salon_names = set()  # 重複を排除するためにセットを使用

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 全角スペースを半角スペースに変換
            row['salonName'] = row['salonName'].replace('\u3000', '　')
            salon_names.add(row['salonName'])

    # セットをリストに変換
    return list(salon_names)