from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists    
import grequests
import requests
import json
from flask import request
from dateutil import parser
from datetime import datetime
# from flask_paginate import Pagination, get_page_args
from apscheduler.schedulers.background import BackgroundScheduler as scheduler
from celery import Celery
import os
API_KEY = os.environ.get('YOUTUBE_API_KEY')


basedir = os.path.abspath(os.path.dirname('./'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


"""
==============
Model
==============
"""
# Video Model Schema
class Video(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(120))
    url = db.Column(db.String(50))
    publishedAt=db.Column(db.DateTime(20))

    def __repr__(self):
        return '<Video %r>' % self.title


"""
==============
Routes
==============
"""
# @route   GET /
# @access  Public
@app.route("/")
def hello_world():
    return "<p>Server is Running !</p>"

# @desc  - search route to list all the video data related to a specific search query and store the data in the Database
#        - In the browser , go to this route before going to the `/result` as this route stores the data in the db
# @route   GET /search
# @access  Public
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
             
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':API_KEY
    }

    request_video = requests.get(video_url,params=v_params)
    video_data=request_video.json()
    video_specific_data={}

    for data in video_data['items']:
        current_data=[]

        current_data.append(data['snippet']['title'])
        current_data.append(data['snippet']['description'])
        current_data.append(data['snippet']['thumbnails']['default']['url'])
        # format dateTime from type String to type DateTime
        date = data['snippet']['publishedAt'].replace("T", " ")
        date_time = date.replace("Z", "")
        formatted_date=datetime.fromisoformat(date_time)
        # Append data to the current_data list
        current_data.append(formatted_date)
        current_data.append({
            'title':data['snippet']['title'],
            'description':data['snippet']['description'],
            'url':data['snippet']['thumbnails']['default']['url'],
            'publishedAt':data['snippet']['publishedAt']
        })
        
        # exists = db.session.query(db.exists().where(Video.id == data['id'])).scalar()
        exists=bool(Video.query.filter_by(id=data['id']).first())
        #Check if the data already exists in the DB
        if(exists!=True):
            #If not exists then Add data to DB 
            db_data = Video(
            id=data['id'],
            title=data['snippet']['title'],
            description=data['snippet']['description'],
            url=data['snippet']['thumbnails']['default']['url'],
            publishedAt=formatted_date
            )

            db.session.add(db_data)
            db.session.commit()    

        video_specific_data['items']=current_data
    return video_data

# returns the stored video data from DB in a paginated response sorted in descending order of published datetime .
# @route   GET /result
# @access  Public
@app.route("/result",methods=['GET'])
def result():

    return jsonify(get_paginated_list_db(
		Video, 
		'/result', 
		start=request.args.get('start', 1), 
		limit=request.args.get('limit', 3)
	))


# returns video data based on specific search query directly from the Youtube Api
# @route   GET /videos
# @access  Public
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
    
    video_specific_data = get_video_list(video_url, v_params)
    return jsonify(video_specific_data)


# @desc    A GET API which returns the video data (directly from the Youtube API) in a         paginated response sorted in descending order of published datetime.
# @route   GET /paginate
# @access  Public
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

    video_specific_data = get_video_list(video_url, v_params)
    
    # paginate the data and store in result

    result= get_paginated_list(
        video_specific_data,
        '/paginate',
        start=request.args.get('start', 1), 
		limit=request.args.get('limit', 20)
        )
    return jsonify(result)

# @desc    returns the video data from the data base in sorted in descending order of published datetime without pagination
# @route   GET /db
# @access  Public
@app.route("/db")
def get_db_data():
    
    videos = Video.query.order_by(Video.publishedAt.desc()).all()
    video_data={}
    current_data=[]

    for video in videos:
        current_data.append({
            'id':video.id,
            'title':video.title,
            'description':video.description,
            'url':video.url,
            'publishedAt':video.publishedAt
        })
    video_data["items"]=current_data
    return jsonify(video_data)
        
    


"""
==============
Functions
==============
"""

# Function to paginate List
def get_paginated_list(results, url, start, limit):
    """Paginates the video data.

    Parameters
    ----------
    results: list
    url : String
    start : String
    limit : String

    Returns
    -------
    [paginated json object]
    """
    start = int(start)
    limit = int(limit)
    count = len(results)
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

    return obj

# Function to get search query result from api
def get_search_list(url,s_params):
    """Data based on a predined search query

    Parameters
    ----------
    url:String
    s_params : Dictionary

    Returns
    -------
    [List of video ids of videos for a predefined search query]
    """
    video_list = []
    
    r=requests.get('https://youtube.googleapis.com/youtube/v3/search',params=s_params)
    data=r.json()
    result = data["items"]
    #Iterate result to store videoId in a list
    for i in result:
        video_list.append(i['id']['videoId'])
         
    return video_list
        
# Function to get video data for a particular search query from api
def get_video_list(url,v_params):
    """Video Data based on predefined search query

    Parameters
    ----------
    url:String
    s_params : Dictionary

    Returns
    -------
    [list of Video Data for the given video ids (params)]
    """
    request_video = requests.get(url,v_params)
    # Serialize the data
    video_data=request_video.json()
    video_specific_data={}
    # create an array to store in the items attribute
    current_data=[]

    for data in video_data["items"]:
        
        current_data.append({
            'title':data['snippet']['title'],
            'description':data['snippet']['description'],
            'url':data['snippet']['thumbnails']['default']['url'],
            'publishedAt':data['snippet']['publishedAt']
        })
                        
    video_specific_data["items"]=current_data
    return current_data

# Function to paginate List , a little different from get_paginated_list()
def get_paginated_list_db(model, url, start, limit):
    """Function returns the stored video data in a paginated response sorted in descending order of published datetime.

    Parameters
    ----------
    results: list
    url : String
    start : String
    limit : String

    Returns
    -------
    [stored video data in a paginated response sorted in descending order of published datetime.]
    Note:
    ------
    get_paginated_list() function also perform the same task , the only difference is in parameters , in this function then `model` parameter is passed which is a DB model. While in the case of get_paginated_list() the parameter is a list object .
    
    Kept both the functions here for understanding purpose .
    """
    
    results = model.query.order_by(Video.publishedAt.desc()).all()
    start = int(start)
    limit = int(limit)
    count = len(results)
    
    #store data from the data base to a list to avoid following error
    #Error : Object of type Video is not JSON serializable
    current_data=[]

    for video in results:
        current_data.append({
            'id':video.id,
            'title':video.title,
            'description':video.description,
            'url':video.url,
            'publishedAt':video.publishedAt
        })
    if (count < start):
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
    obj['results'] = current_data[(start - 1):(start - 1 + limit)]
    return obj



# # This Code runs a particular function in the background after a set interval
# # Run Scheduler every 10 sec
# sch = scheduler()
# sch.add_job(paginate, 'interval', seconds=10)
# sch.start()
