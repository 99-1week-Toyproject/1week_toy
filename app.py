from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(
    'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20210829', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

client = MongoClient(
    'mongodb+srv://hyeunseung:qlqjsgustmd1)@cluster0.jwlfweq.mongodb.net/?retryWrites=true&w=majority')
db = client.Practice


@app.route('/')
def home():
    return render_template('board.html')


@app.route("/board/get", methods=["GET"])
def board_get():
    board_list = list(db.gameReview.find({}, {'_id': False}))

    return jsonify({'board_list': board_list})


@app.route("/board/post", methods=["POST"])
def board_post():
    board_title_receive = request.form['board_title_give']
    board_id_receive = request.form['board_id_give']
    board_text_receive = request.form['board_text_give']

    board_list = list(db.gameReview.find({}, {'_id': False}))
    board_cnt = len(board_list) + 1

    insertDoc = {
        'index': board_cnt,
        'title': board_title_receive,
        'id': board_id_receive,
        'text': board_text_receive
    }

    db.gameReview.insert_one(insertDoc)

    return jsonify({'msg': "등록완료"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
