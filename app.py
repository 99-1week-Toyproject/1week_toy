# 해시함수 사용을 위한 hashlib 모듈 설치
import hashlib
# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime
# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt
from pymongo import MongoClient
from flask import Flask, redirect, render_template, request, jsonify, url_for, session
import certifi
from bs4 import BeautifulSoup
import requests

ca = certifi.where()

app = Flask(__name__)


# JWT 시크릿 키 입니다.
OUR_SECRET_KEY = 'TEAM12'

##########################################################
## 담당자의 변)                                                                            ##
## jinja2 이용했으면 동적부분을 더 쉽게 빠르게 바꾸는 게 가능했을텐데..  ##
## 너무 늦게 알았습니다..                                                               ##
##########################################################

##########################
## HTML 넘기는 부분             ##
##########################

client = MongoClient(
    'mongodb+srv://hyeunseung:qlqjsgustmd1)@cluster0.jwlfweq.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.Practice


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/login')
def login():
    # 정보를 가져올때,이 args를 사용한다.
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/board', methods=['GET'])
def board():

    token_receive = request.cookies.get("userToken")

    try:
        payload = jwt.decode(token_receive, OUR_SECRET_KEY,
                             algorithms=['HS256'])
        user_info = db.gameReview_user.find_one({"id": payload['id']})
        return render_template('board.html', id=user_info['id'])

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))


@app.route('/main', methods=['GET'])
def main():
    token_receive = request.cookies.get("userToken")

    try:
        payload = jwt.decode(token_receive, OUR_SECRET_KEY,
                             algorithms=['HS256'])
        user_info = db.gameReview_user.find_one({"id": payload['id']})
        return render_template('main.html', id=user_info['id'])

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))


@app.route("/board/get", methods=["GET"])
def board_get():
    board_list = list(db.gameReview.find({}, {'_id': False}))

    return jsonify({'board_list': board_list})


@app.route("/board/post", methods=["POST"])
def board_post():
    board_title_receive = request.form['board_title_give']
    board_id_receive = request.form['board_id_give']
    board_text_receive = request.form['board_text_give']
    board_cntValue_receive = request.form['board_cntValue_give']

    board_list = list(db.gameReview.find({}, {'_id': False}))
    board_cnt = len(board_list) + 1

    insertDoc = {
        'index': board_cnt,
        'title': board_title_receive,
        'id': board_id_receive,
        'text': board_text_receive,
        'cntValue': board_cntValue_receive
    }

    db.gameReview.insert_one(insertDoc)

    return jsonify({'msg': "등록완료"})


@app.route("/board/post/reply", methods=["POST"])
def board_post_reply():
    reply_name_receive = request.form['reply_name_give']
    reply_text_receive = request.form['reply_text_give']
    reply_index_receive = request.form['reply_index_give']

    insertDoc = {
        'index': int(reply_index_receive),
        'name': reply_name_receive,
        'text': reply_text_receive
    }

    db.gameReview_reply.insert_one(insertDoc)

    return jsonify({'msg': "등록완료"})


@app.route("/board/get/reply", methods=["GET"])
def board_get_reply():
    board_reply_list = list(db.gameReview_reply.find({}, {'_id': False}))

    return jsonify({'board_reply_list': board_reply_list})


##################################################
## 구현되지 않은 댓글 카운트 기능에 대한 단락입니다             ##
## 해당 파트는 제가 추후에 업데이트 할 것입니다                  ##
##################################################
# @app.route("/board/get/reply/cnt", methods=["GET"])
# def board_get_reply_cnt():
#     ########################일단 리스트 다 가져옴
#     board_reply_list = list(db.gameReview_reply.find({}, {'_id': False}))
#     board_post_list = list(db.gameReview.find({},{'_id':False}))

# ########################잘 나오나?
#     print(board_reply_list)
#     print(board_post_list)

# #######################댓글의 인덱스 번호를 가져옴
#     board_reply_cntList = []

#     for board_reply_listed in board_reply_list:
#         print(board_reply_listed)
#         board_reply_cntList.append(board_reply_listed['index'])

#     print(board_reply_cntList)

    # return jsonify({'board_reply_list': board_reply_list})


##########################
## 로그인을 위한 API              ##
##########################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/join/idCheck', methods=['POST'])
def api_join_idCheck():
    join_ID_receive = request.form['join_IDcheck_give']

    all_users = list(db.gameReview_user.find({}, {'_id': False}))
    all_users_id = []

    for all_user in all_users:
        all_users_id.append(all_user['id'])

    print(all_users_id)
    print(join_ID_receive)

    if join_ID_receive in all_users_id:
        return jsonify({'result': 'fail'})
    else:
        return jsonify({'result': 'success'})


@app.route('/join', methods=['POST'])
def api_join():
    join_ID_receive = request.form['join_ID_give']
    join_PW_receive = request.form['join_PW_give']

    pw_hash = hashlib.sha256(join_PW_receive.encode('utf-8')).hexdigest()

    all_users = list(db.gameReview_user.find({}, {'_id': False}))
    all_users_id = []

    for all_user in all_users:
        all_users_id.append(all_user['id'])

    print(all_users_id)
    print(join_ID_receive)

    if join_ID_receive in all_users_id:
        return jsonify({'result': 'fail', 'msg': '중복된 ID입니다ㅠ'})
    else:
        db.gameReview_user.insert_one(
            {'id': join_ID_receive, 'pw': pw_hash})
        return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/login/api', methods=['POST'])
def api_login():
    login_id_receive = request.form['login_id_give']
    login_pw_receive = request.form['login_pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(login_pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    login_result = db.gameReview_user.find_one(
        {'id': login_id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if login_result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': login_id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, OUR_SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다!'})


@app.route('/login/validCheck', methods=['GET'])
def login_valid():
    token_receive = request.cookies.get('userToken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive,
                             OUR_SECRET_KEY,
                             algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.gameReview_user.find_one(
            {'id': payload['id']}, {'_id': False})
        return jsonify({'result': 'success', 'id': userinfo['id']})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})

############################
## 메인페이지 크롤링 파트입니다 ##
############################

# bs4 관련 네이밍 앞에 게임관련으로 변경하였습니다!
# 데이터베이스 collection은 gameList로 설정하였습니다!


db.gameList.delete_many({})

# URL을 읽어서 HTML를 받아오고,
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
gamedata = requests.get(
    'https://www.gamemeca.com/ranking.php', headers=headers)

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
gameSoup = BeautifulSoup(gamedata.text, 'html.parser')

# select를 이용해서, tr들을 불러오기
games = gameSoup.select(
    '#content > div.ranking_list > div.rank-list > div.content-left > table > tbody > tr')

# games (tr들) 의 반복문을 돌리기
for game in games:
    # game 안에 a 가 있으면,
    rank = game.select_one('span.rank').text
    name = game.select_one('div.game-name > a').text
    img = game.select_one('img')['src']
    doc = {
        'rank': rank,
        'name': name,
        'img': img,
        'star': 0,
        'people': 0,
        'average': 0
    }
    db.gameList.insert_one(doc)
#    if name is not None:
#       print(rank, name, img)


@app.route("/main/posts", methods=["GET"])
def gameList_get():
    games_list = list(db.gameList.find({}, {'_id': False}))
    return jsonify({'games': games_list})


@app.route("/main/star", methods=["POST"])
def star_post():
    star_receive = request.form["star_give"]
    rank_receive = request.form["rank_give"]
    target = db.gameList.find_one({'rank': rank_receive})
    target_people = target['people']
    target_new_people = target_people + 1

    target_star = target['star']
    star_receive = float(star_receive)
    target_new_star = target_star + star_receive

    target_average = target['average']
    target_new_average = target_new_star/target_new_people

    db.gameList.update_one({'rank': rank_receive}, {'$set': {
        'people': target_new_people, 'star': target_new_star, 'average': target_new_average}})

    return jsonify({'msg': '등록 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
