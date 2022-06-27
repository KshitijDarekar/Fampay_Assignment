
# Backend Assignment (Intern) | FamPay


# Project Goal

To make an API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.


## Features

- Fetching the latest videos for a predefined search query and should store the data of vid eos (specifically these fields - Video title, description, publishing datetime, thumbnails URLs and any other fields you require)



## Tech Stack

**Flask**

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file.You can refer the samp.env file

`YOUTUBE_API_KEY=`


## Run Locally

Clone the project

```bash
  git clone https://github.com/KshitijDarekar/Fampay_Assignment.git
```

Go to the project directory

```bash
  cd <project-directory>
```
Setup virtual environment
```
$ python3 -m venv venv

```
Activate venv
```
$ . venv/bin/activate

```
Install Flask
```
$ pip install Flask

```
Install dependencies

```bash
$ pip install -r requirements.txt  (for python 2.x)

$ pip3 install -r requirements.txt (for python 3.x)
```

Set flaskenv and 
```bash
$ export FLASK_APP=server
$ export FLASK_ENV=development


```
Run Flask server
```
$ flask run
```
Check the route /paginate to view paginated api
Check

## Routes

```javascript
localhost:5000/paginate
returns paginated response
```
```
localhost:5000/videos
list the details of fetched videos based on a particular search query
```

