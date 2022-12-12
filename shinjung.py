from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


client = MongoClient(
    'mongodb+srv://test:sparta@cluster0.7v9fhz8.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta
db.games.delete_many({})

# URL을 읽어서 HTML를 받아오고,
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.gamemeca.com/ranking.php', headers=headers)

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
soup = BeautifulSoup(data.text, 'html.parser')

# select를 이용해서, tr들을 불러오기
games = soup.select(
    '#content > div.ranking_list > div.rank-list > div.content-left > table > tbody > tr')

# movies (tr들) 의 반복문을 돌리기
for game in games:
    # movie 안에 a 가 있으면,
    rank = game.select_one('span.rank').text
    name = game.select_one('div.game-name > a').text
    img = game.select_one('img')['src']
    doc = {
        'rank': rank,
        'name': name,
        'img': img
    }
    db.games.insert_one(doc)
#    if name is not None:
#       print(rank, name, img)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/posting", methods=["GET"])
def bucket_get():
    games_list = list(db.games.find({}, {'_id': False}))
    return jsonify({'games': games_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
