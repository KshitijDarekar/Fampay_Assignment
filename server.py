from flask import Flask
import requests
import json

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# search route to list all data related to a specif search query
@app.route("/search")
def search():
    s_params={
        'part':'snippet',
        'maxResults':'2',
        'q':'cricket',
        'type':'video',
        'key':'AIzaSyCm3jzacen7NmjX5_2TrWPeAbp_AXLIDSk'
    }
    video_list = []
    
    r=requests.get('https://youtube.googleapis.com/youtube/v3/search',params=s_params)
    data=r.json()
    # print(data['items'][0]['id']['videoId'])
    result = data['items']
    
    for i in result:
        video_list.append(i['id']['videoId'])
        
    
#    nv2wpxFVpHU     
    print(video_list)
    
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':'AIzaSyCm3jzacen7NmjX5_2TrWPeAbp_AXLIDSk'
    }

    # for i in data:
    #     for vdata[] in i:
    #         print("i=",vdata)
    # print(data)
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
        'maxResults':'4',
        'q':'cricket',
        'type':'video',
        'key':'AIzaSyCm3jzacen7NmjX5_2TrWPeAbp_AXLIDSk'
    }
    video_list = []
    r=requests.get('https://youtube.googleapis.com/youtube/v3/search',params=s_params)
    data=r.json()
    # print(data['items'][0]['id']['videoId'])
    result = data['items']
    
    for i in result:
        video_list.append(i['id']['videoId'])
        
    
#    nv2wpxFVpHU     
    print(video_list)
    
    video_url = 'https://youtube.googleapis.com/youtube/v3/videos'
    v_params = {
        'part':'snippet',
        'id':video_list,
        'key':'AIzaSyCm3jzacen7NmjX5_2TrWPeAbp_AXLIDSk'
    }

    # for i in data:
    #     for vdata[] in i:
    #         print("i=",vdata)
    # print(data)
    # fetch data from video url
    request_video = requests.get(video_url,params=v_params)
    video_data=request_video.json()
    video_limited_data={}
    # create an array to store in the items attribute
    current_data=[]

    for data in video_data['items']:
        # current_data.append(data['snippet']['title'])
        # current_data.append(data['snippet']['description'])
        # current_data.append(data['snippet']['thumbnails']['default']['url'])
        # current_data.append(data['snippet']['publishedAt'])
        # Add selected data to the list
        current_data.append({
            'title':data['snippet']['title'],
            'description':data['snippet']['description'],
            'url':data['snippet']['thumbnails']['default']['url'],
            'publishedAt':data['snippet']['publishedAt']
        })
                
    video_limited_data['items']=current_data
        
        # print("data=",data['snippet']['title'],data['snippet']['description'],data['snippet']['thumbnails']['default']['url'],data['snippet']['publishedAt'])
        # print(json.dumps(current_data,indent=4,sort_keys=True))
        
    
    # print(json.dumps(video_data, indent=4, sort_keys=True))
    # return video_data
    print(json.dumps(video_limited_data, indent=4, sort_keys=True))
    return video_limited_data

