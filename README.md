# JogTrack: Rest API built with Python 3.5, Django, Postgres

The API purpose is to store user's jogging times.

## Endpoints
The API exposes the following endpoints:
##### User related endpoints
- **/users/register/** - User registration(POST). The reponse contains an authentication token that will be further used to authenticate user's requests. The token expires after 24h.
- **/users/login/** - User login(POST). The reponse contains an authentication token that will be further used to authenticate user's requests. The token expires after 24h.
- **/users/** - User list(GET) and create(POST). This endpoint has filtering capabilities when providing 'search' query parameter with GET requests (?search=$FILTER). Regular users are not allowed to access this endpoint.
- **/users/<user_id>/** - User retrieve(GET), update(PUT/PATCH) and delete(DELETE).

##### Jogs related endpoints
- **/jogs/** - Jog list(GET) and create(POST).
- **/jogs/<jog_id>/** - Jog retrieve(GET), update(PUT/PATCH) and delete(DELETE).
- **/jogs/reports/** - Jog Reports retrieve (GET).

##### Notes
- When creating/updating a jog, based on the provided date and location, the API connects to a weather API from worldweatheronline.com and gets the weather conditions for the run (temperature, feels_like, precipitation, humidity, clouds cover and weather description). For API authentication a token is used (configured in /jogtrack/jogtrack/settings/base.py - WEATHER_API_KEY), generated as part of a trial account (for 1 month).


## Permissions
The application has three level of permissions:
- **Regular users**: can CRUD on their owned records (account and jogs)
- **Manager users**: can CRUD users and their owned jogs. NOTE: Managers can't crude Admin users
- **Admin users**: can CRUD any users and jogs.

## Filtering
- the API provides filter capabilities for all endpoints that return a list of elements (**/users/**, **/jogs/**, **/jogs/reports/**)
- filering is enabled when 'search' query parameter is provided to the URL: eg. **/users?search=user__pk eq 10**
- the API filtering allows using parenthesis for defining operations precedence
- when definig filters, the supported operations include **OR**, **AND**, **eq** (equals), **ne** (not equals), **gt** (greater than), **gte** (greater than or equals), **lt** (lower than), **lte** (lower than or equals)
- **Example**: /jogs?search=(date eq 2016-05-01) AND ((distance gt 20) OR (distance lt 10))

Based on endpoint type, the following filters are available:
- **/jogs/**: user__pk, date, distance, time, country, city
- **/jogs/reports/**: id, user__pk, start_date, end_date 
- **/users/**: id, role, username, email

## Pagination
- the API provides pagination for all endpoints that return a list of elements (**/users/**, **/jogs/**, **/jogs/reports/**)
- the default page size is 10. To configure a diferent value, change `PAGE_SIZE` variable from /jogtrack/jogtrack/settings/base.py
- Each response contains a "count" field that represents the total number of entries (without being restricted by the page size), a "next" field with the URL for the next page, a "previous" with the URL for the previous page, and a 'results' field with the serialized entries, up to the PAGE_SIZE count.
## Running the App

**Prerequisites**
- docker
- docker-compose

**How to run**
1. Create your own local.py file using local.sample in /jogtrack/jogtrack/settings folder and replace `DATABASE_USER`, `DATABASE_PASS`, `YOUR_IP` (get the IP address of your wireless or wired interface `ifconfig` )
2. `cd jogtrack`
3. `sudo docker-compose up --build` (For the first time use --build parameter to generate the docker image, after that run the command without it)

## Run Automated Tests
```
sudo docker exec -it $(sudo docker ps -qf "name=jogtrack_web") python manage.py test users.tests
sudo docker exec -it $(sudo docker ps -qf "name=jogtrack_web") python manage.py test jogs.tests
sudo docker exec -it $(sudo docker ps -qf "name=jogtrack_web") python manage.py test utils.services.tests
```

## Run Manual Tests
The easiest way to manually test is to use **Swagger interface** which is available under **/swagger/** path. It exposes all the endpoints, with all the fields. In order to make an authenticated request, you have to press on Authorize button and provide a user token (got from a user login or a user register request) in the **value** input field. The token has to have the following format: **Token $actual_token_hash**

Also, you can install **Advanced REST Client** plugin in Chrome and open it.

**NOTE**: there is a root admin user that is automatically created (admin/password) that can access the /admin/ interface.
Also, some regular, manager and admin users are automatically created as well. Their username and passwords are in users/fixtures/users.json.

#### User Registration Example
- user **POST** Method, and URL: **http://127.0.0.1:8000/users/register/**
- in Header section, add **content-type** **application/json**
- in Body section add the following json:
```
{
    "username": "myuser",
    "email": "myuser@gmail.com",
    "password": "MyuserStrong1!",
    "confirm_password": "MyuserStrong1!"
}
```
- Save the authentication token received in the response, in order to authenticate the user for the following requests.

#### User Login Example
- use **POST** Method, and URL: **http://127.0.0.1:8000/users/login/**
- in Header section, add **content-type** **application/json**
- in Body section add the following json:
```
{
    "username": "myuser",
    "password": "MyuserStrong1!"
}
```
- Save the authentication token received in the response, in order to authenticate the user for the following requests.

#### Create Jog Example
- use **POST** Method, and URL: **http://127.0.0.1:8000/jogs/**
- in Header section, add **content-type** header name with **application/json** value and **Authorization** header name with **Token 17fcad11819152d11c58037a234ca3e582778b39** value (Note: don't forget the 'Token' word in front of the hashed token)
- in Body section add the following json (NOTE: **location** has *"$City,$Country"** format and **date** has **YYYY-MM-DD** format):
```
{
  "date": "2020-05-04",
  "distance": 5000,
  "time": 1800,
  "location": "Bucharest, Romania"
}
```
#### List & Filter Jog Example
- use **GET** Method, and URL: **http://127.0.0.1:8000/jogs?search=(date gte 2020-05-01) AND ((distance lt 8000) OR (city eq Bucharest))**
- in Header section, add **content-type** header name with **application/json** value and **Authorization** header name with **Token 17fcad11819152d11c58037a234ca3e582778b39** value (Note: don't forget the 'Token' word in front of the hashed token)
