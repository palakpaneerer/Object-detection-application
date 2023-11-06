# ライブラリーのインポート
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from array import array
import os
from PIL import Image
import sys
import time
import json
import streamlit as st
from PIL import ImageDraw
from PIL import ImageFont


# 秘密鍵、エンドポイントの情報を含むJSONファイルの読み込み
with open('secret.json') as f:
    secret = json.load(f)


# Azureの認証情報の設定、ログイン
KEY = secret['KEY']
ENDPOINT = secret['ENDPOINT']
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))


# 関数化（画像内のオブジェクトの名前）
def detect_objects(filepath):
    local_image = open(filepath, "rb")
    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    objects = detect_objects_results.objects
    return objects


# 関数化（タグ情報の取得）
def get_tags(filepath):
    local_image = open(filepath, "rb")
    tags_result = computervision_client.tag_image_in_stream(local_image)
    tags = tags_result.tags
    tags_name = []
    for tag in tags:
        tags_name.append(tag.name)
    return tags_name


# ここからstreamlitのコード
# タイトル
st.title('物体検出アプリ')


# 画像をアップロード
uploaded_file = st.file_uploader('Choose an image...', type=['jpg', 'png'])

# 画像アップロード後の処理
if uploaded_file is not None:
    img = Image.open(uploaded_file)


    # 関数を使うのにfilepathが欲しいので、uploaded_fileで読み込んだ写真を
    # あるフォルダに保存してそのpathを抽出する。
    img_path = f'img/{uploaded_file.name}'
    img.save(img_path)


    # 関数実行(画像内のオブジェクトの名前)
    objects = detect_objects(img_path)

    # 描画
    draw = ImageDraw.Draw(img)
    for object in objects:

        # 必要な情報の取得
        x = object.rectangle.x
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        caption = object.object_property

        font = ImageFont.truetype(font='./Helvetica 400.ttf', size=50)
        text_w, text_h = draw.textsize(caption, font=font)

        draw.rectangle([(x, y), (x+w, y+h)], fill=None, outline='green', width=5) 
        draw.rectangle([(x, y), (x+text_w, y+text_h)], fill='green')
        draw.text((x, y), caption, fill='white', font=font)


    # web画面上に表示
    st.image(img)

    # web画面上に表示
    st.markdown('**認識されたコンテンツタグ**')

    #関数実行(タグ情報取得)
    tags_name = get_tags(img_path)
    # リスト→要素1, 要素2という表示に変える。
    tags_name = ', '.join(tags_name)

    st.markdown(f'> {tags_name}')   
