from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.msaktnw.mongodb.net/cluster0?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/game", methods=["POST"])
def game_post():
    game_receive = request.form['game_give']

    game_list = list(db.game.find({}, {'_id': False}))
    count = len(game_list) + 1

    doc = {
        'num': count,
        'game': game_receive,
        'done': 0
    }

    db.game.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


@app.route("/game", methods=["GET"])
def game_get():
    game_list = list(db.game.find({}, {'_id': False}))
    return jsonify({'games': game_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
