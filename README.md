# Template Manager

Template Manager is website for managing templates



## Technologies

- [Python 3.9](https://python.org): Base programming language for development
- [Flask](https://flask.palletsprojects.com/): Development framework used for the application
- [MongoDB](https://www.mongodb.com/): A NoSQL Database that serves it purpose
- [Github Actions](https://docs.github.com/en/free-pro-team@latest/actions) : Continuous Integration and Deployment

## How To Start App

- Clone the Repository
```
git clone https://github.com/Afeezagbaje/Template-Manager.git
```
- Then run the following commands consecutively
```
python3 -m venv venv 
```
- To activate virtual environment (MacOS users): 
```
source venv/bin/activate
```
- To activate virtual environment (Windows users):
```
source venv/Source/activate
```
- Install dependencies as follows (both MacOS & Windows):
```
pip3 install -r requirements.txt
```
- Adding dependences by following the below in succession:
    - create a .env file using .env.example to configure  
- Run server
```
flask run
```

- Running the above command will Start up the following Servers:
    - Flask Development Server --> http://localhost:5000
    - MongoDB Server --> http://localhost:27017

## Exploring The App

Make sure that all the above servers are running before you start exploring the project. If those servers are up and running, have fun with the app!!!

### API

You can explore the TemplateManager App by going to `http://localhost:5000` on your browser. The following endpoints are accessible

1. POST register user --> `http://localhost:5000/api/v1/auth/register`
2. POST login user --> `http://localhost:5000/api/v1/auth/login`
3. GET All Templates --> `http://localhost:5000/api/v1/template`
4. GET Single Template --> `http://localhost:5000/api/v1/template/<id>`
5. PUT Single Template --> `http://localhost:5000/api/v1/template/<id>`
6. DELETE Single Template --> `http://localhost:5000/api/v1/template/<id>`
7. GET Refresh Token --> `http://localhost:5000/api/v1/auth/token/refresh`

