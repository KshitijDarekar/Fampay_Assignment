from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists    

import grequests
import requests
import json
from flask import request
# from flask_paginate import Pagination, get_page_args
from apscheduler.schedulers.background import BackgroundScheduler as scheduler
from celery import Celery
import os
API_KEY = os.environ.get('YOUTUBE_API_KEY')


basedir = os.path.abspath(os.path.dirname('./'))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
# print("base dir =  ",os.basedir)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)
# app.config['CELERY_BROKER_URL']     = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

class Video(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(120))
    url = db.Column(db.String(50))
    publishedAt=db.Column(db.String(20))

    def __repr__(self):
        return '<Video %r>' % self.title

# db.create_all()

# @app.route
# @celery.task
# def my_background_task(arg1, arg2):
#     # some long running task here
#     return "Hello , I am running asynchrounously"

# task = my_background_task.delay(10, 20)

# task = my_background_task.apply_async(args=[10, 20], countdown=30)


@app.route("/")
def hello_world():
    return "<p>Server is Running !</p>"

# search route to list all the video data related to a specific search query
@app.route("/search")
def search():
    s_params={
        'part':'snippet',
        'maxResults':'10',
        'q':'cricket',
        'type':'video',
        'key':API_KEY
    }
    video_list = []
    
    r=requests.get('https://youtube.googleapis.com/youtube/v3/search',params=s_params)
    data=r.json()
    result = data['items']
    
    for i in result:
        video_list.append(i['id']['videoId'])
         
    print(video_list)
    
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':API_KEY
    }

    request_video = requests.get(video_url,params=v_params)
    video_data=request_video.json()
    video_limited_data={}
    for data in video_data['items']:
        current_data=[]

        current_data.append(data['snippet']['title'])
        current_data.append(data['snippet']['description'])
        current_data.append(data['snippet']['thumbnails']['default']['url'])
        current_data.append(data['snippet']['publishedAt'])
        
        current_data.append({
            'title':data['snippet']['title'],
            'description':data['snippet']['description'],
            'url':data['snippet']['thumbnails']['default']['url'],
            'publishedAt':data['snippet']['publishedAt']
        })
        
        # exists = db.session.query(db.exists().where(Video.id == data['id'])).scalar()
        exists=bool(Video.query.filter_by(id=data['id']).first())
        print("exists: \n",exists)
        #Check if the data already exists in the DB
        if(exists!=True):
            #Add data to DB 
            db_data = Video(
            id=data['id'],
            title=data['snippet']['title'],
            description=data['snippet']['description'],
            url=data['snippet']['thumbnails']['default']['url'],
            publishedAt=data['snippet']['publishedAt']
            )

            db.session.add(db_data)
            db.session.commit()    



                
        video_limited_data['items']=current_data
        
        print("data=",data['snippet']['title'],data['snippet']['description'],data['snippet']['thumbnails']['default']['url'],data['snippet']['publishedAt'])
        print(json.dumps(current_data,indent=4,sort_keys=True))
        
    
    # print(json.dumps(video_data, indent=4, sort_keys=True))
    # return video_data
    print(json.dumps(video_limited_data, indent=4, sort_keys=True))
    return video_data

# returns list of video api with required data based on search query
@app.route("/videos")
def videos():
    s_params={
        'part':'snippet',
        'maxResults':'10',
        'q':'football',
        'type':'video',
        'key':API_KEY
    }

    video_list = get_search_list('https://youtube.googleapis.com/youtube/v3/search', s_params)
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':API_KEY
    }
    
    video_limited_data = get_video_list(video_url, v_params)
    return video_limited_data


@app.route("/paginate",methods=['GET'])
def paginate():
    
    # Get search data
    search_url='https://youtube.googleapis.com/youtube/v3/search'
    s_params={
        'part':'snippet',
        'maxResults':'10',
        'q':'football',
        'type':'video',
        'key':API_KEY
    }
    # store video_id from get_search_list in video_list
    video_list = []
    video_list = get_search_list(search_url, s_params)
    # get video data for the particular queries
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':API_KEY
    }
#['eECgSJis8jM', 'QXhV148EryQ', 'xnqCrnYBz2U', 'Cf3vKcxmc-A', '8_sq4qcf20I', 'kWE1mHBATj0', 'LEc7W2C6kcM', 'vTVuB1kgpd4', 'HL8Er3cP2b4', '1p0yFxZhKfo']
    video_limited_data = get_video_list(video_url, v_params)
    print(json.dumps(video_limited_data))
    # print(json.dumps(video_data, indent=4, sort_keys=True))
    # return video_data
    print(json.dumps(video_limited_data, indent=4, sort_keys=True))
    
    # paginate the data and store in result
    print("typeof current_data =" ,type(video_limited_data))
    print("typeof json.dumps(current_data) =" ,type(json.dumps(video_limited_data)))
    
    result= get_paginated_list(video_limited_data, 'localhost:5000/paginate', '2', '3')
    print("result=",result)
    return result

@app.route("/db")
def get_db_data():
    data = Video.query.all()
    print("data = \n",json.dumps(data))
    return "Hello"
        
    

# Function to paginate List
def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    print("count",count)
    if count < start or limit < 0:
        abort(404)
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    print("type of results: ",type(results))
    print("Result==",json.dumps(results[1:11]))
    
    print("Obj==",json.dumps(obj))
    return obj

# Function to get search query result from api
def get_search_list(url,s_params):
    
    video_list = []
    
    r=requests.get('https://youtube.googleapis.com/youtube/v3/search',params=s_params)
    data=r.json()
    result = data["items"]
    
    for i in result:
        video_list.append(i['id']['videoId'])
         
    print("search list function : ",video_list)
    return video_list
        
# Function to get video data for a particular search query from api
def get_video_list(url,v_params):
    
    request_video = requests.get(url,v_params)
    
    video_data=request_video.json()
    # print("raw data =",video_data)
    video_limited_data={}
    # create an array to store in the items attribute
    current_data=[]

    for data in video_data["items"]:
        
        current_data.append({
            'title':data['snippet']['title'],
            'description':data['snippet']['description'],
            'url':data['snippet']['thumbnails']['default']['url'],
            'publishedAt':data['snippet']['publishedAt']
        })
                
    print("Current DATA : ", json.dumps(current_data,indent=4))           
    video_limited_data["items"]=current_data
    print("current data 1st element:",json.dumps(current_data[0],indent=4))
    return current_data


# Run Scheduler every 10 sec
# sch = scheduler()
# sch.add_job(paginate, 'interval', seconds=10)
# sch.start()
