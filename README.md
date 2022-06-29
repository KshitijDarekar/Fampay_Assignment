
# Backend Assignment (Intern) | FamPay


# Project Goal

To make an API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.


## Features

- Fetching the latest videos for a predefined search query and should store the data of vid eos (specifically these fields - Video title, description, publishing datetime, thumbnails URLs and any other fields you require)

- A GET API which returns the stored video data in a paginated response sorted in descending order of published datetime.



## Tech Stack

**▷Flask**  
**▷Flask-SQLAlchemy**  
**▷SQLite**

## Environment Variables

> To run this project, you will need to add the following environment variables to your .env file.You can refer the samp.env file.

`YOUTUBE_API_KEY=`**enter your api key here without space**


##Installation and  Run Locally

##### Clone the project

```bash
  git clone https://github.com/KshitijDarekar/Fampay_Assignment.git
```

##### Go to the project directory

```bash
  cd Fampay_Assignment

```
##### Setup virtual environment
###### macOS/Linux
```
python3 -m venv venv

```
###### Windows
```
py -3 -m venv venv

```

##### Activate venv
###### macOS/Linux

```
 . venv/bin/activate

```
###### Windows
```
 venv\Scripts\activate
```
##### Install Flask
```
$ pip install Flask

```
##### Install dependencies
###### (for python 2.x)
```bash
$ pip install -r requirements.txt  
```
###### (for python 3.x)
```bash
$ pip3 install -r requirements.txt (for python 3.x)
```

##### Set flaskenv
> Run the following commands based on the terminal you are using

###### Bash
```bash
export FLASK_APP=server
export FLASK_ENV=development
```
###### CMD
```bash
set FLASK_APP=server
set FLASK_ENV=development
```
###### PowerShell
```bash
$env:FLASK_APP = "server"
$env:FLASK_ENV = "development"
```

##### Run Flask server
```
$ flask run
```
##### Setup Database
> ###### Open new terminal in the same directory and run the following lines in the command line

```
$ flask shell
```
###### Now Inside the flask shell to create the  database model
```
>>> from server import db
>>> db.create_all()

```


## Routes / API Reference

| Route  | Desc  | Method  | Note  |
| ------------ | ------------ | ------------ | ------------ |
|  `/search` | search route to list all the video data related to a specific search query and store the data in the Database  |  GET |go to this route before going to the `/result` as this route stores the data in the db   |
|  `/result` | returns the **stored video data** from DB in a **paginated response** sorted in **descending order** of published datetime   |  GET | This is the expected result  |
|  `/videos` | returns video data based on specific search query directly from the Youtube Api  |  GET |   |
|  `/paginate` | returns the video data (**directly from the Youtube API**) in a         **paginated response** sorted in descending order of published datetime. |  GET |   |
|  `/db` |  returns the video data from the data base sorted in descending order of published datetime **without pagination** |   GET|  returns data from db |

                
----

## Acknowledgements / References

- https://help.parsehub.com/hc/en-us/articles/217751808-API-Tutorial-How-to-get-run-data-using-Python-Flask

- https://pypi.org/project/requests/

- https://stackoverflow.com/questions/44138848/make-api-request-every-x-seconds-in-python-3

- https://flask-restless.readthedocs.io/en/latest/sorting.html

- https://stackoverflow.com/questions/55543011/flask-restful-pagination

- https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

- https://flask.palletsprojects.com/en/2.1.x/patterns/sqlalchemy/
- YouTube data v3 API: [https://developers.google.com/youtube/v3/getting-started](https://developers.google.com/youtube/v3/getting-started)
- Search API reference: [https://developers.google.com/youtube/v3/docs/search/list](https://developers.google.com/youtube/v3/docs/search/list)

----


