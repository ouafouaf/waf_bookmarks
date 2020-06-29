# WAF Bookmarks

A simple Flask based bookmark manager. Uses flask, flask-sqlalchemy, flask-migrate, flask-wtf.

## Demo

http://wafwaf.pythonanywhere.com/   

## Getting Started

On linux, follow these steps:   
```
git clone https://github.com/ouafouaf/waf_bookmarks.git
pip install -r requirements.txt
```
Rename `.flaskenv_exemple` to `.flaskenv`. This file is used to store environment variables. Flask will know to find them here thanks to python-dotenv.  
  
Rename `config_exemple.py` (in the app/ directory) to `config.py` and edit the content for your needs.  
  
```
flask db init
flask db migrate -m 'create tables'
flask db upgrade
flask run
```
You should be good to go!  

## To do
  
- Fix bugs  
- Fix all the bugs  
- Login authentication  
- Maybe add multiple tag filters  
