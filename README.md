# Recommendations With IBM Webapp

This repository is a part of https://github.com/herrfeder/DataScientist/tree/master/Project_04_Recommendations_With_IBM .
It serves as a submodule for modular hosting of the webapp for this project.

## Screenshots

| Control Panel and Recommendation Area | Wordcloud and Most Similiar Users |
|--------------------------------------|--------------------------------------|
| ![](screenshots/recommendations_webapp_top.png) | ![](screenshots/recommendations_webapp_bottom.png) |

## Purpose

This webapp should provide a usable use-case for an recommendation engine. Therefore it combines multiple options of recommendation:
  - Singular Value Decomposition (SVD) based recommendation of similiar users.
  - Content Based recommendation based on an NLP Pipeline for similiar articles.
  - Simple Popularity based recommendation for new users.
  
It will show to the user:
  - the choosen number of recommendations for specific user or article
  - the most often occured words of the title in a wordcloud
  - the most similiar users
  

## Included Files
  
  * __Dockerfile__: Files for setting up Docker container
  * __app/data/process_data__: Script for ETL-Pipeline
  * __app/data/disaster_categories.csv__: Source data categories
  * __app/data/disaster_messages.csv__: Source data messages
  * __app/data/DisasterResponse.db__: Resulting SQLite Database
  * __app/models/train_classifier.py__: Script for ML-Pipeline (Training and Storing)
  * __app/static/__: Example images from wikipedia and bootstrap css
  * __run.py__: Dash webapp
  * __wsgi.py__: Gunicorn Wrapper

## Webapp

An example of this web app is temporary accessible on https://federland.dnshome.de/recommendations .
Please be gentle, the resources are restricted. This app __isn't responsive__.

### Docker Instructions:
1. Create directory and download Dockerfile:
    ```
    mkdir pipeline_docker && cd pipeline_docker
    wget https://raw.githubusercontent.com/herrfeder/Udacity-Project-Disaster-Response-Pipelines-Webapp/master/Dockerfile
    ```

2. Build Docker Container:
    ```
    docker build . -t pipeline_docker
    ```
    As the model will be trained during Build, this will take a while.
    
3. Run Docker Container:
    ```
    docker run -p 5000:5000 pipeline_docker:latest
    ```

4. Go to http://0.0.0.0:5000/disasterresponse

### Manual Instructions:
1. Clone this Repository and move into it:
    ```
    git clone https://github.com/herrfeder/Udacity-Project-Disaster-Response-Pipelines-Webapp
    cd Udacity-Project-Disaster-Response-Pipelines-Webapp
    ```

2. Resolve all required Python Packages:
    ```bash
    pip install numpy==1.17
    pip install scipy
    pip install Flask==1.0.0
    pip install pandas==1.0.0
    pip install matplotlib
    pip install scikit_learn
    pip install nltk
    pip install sqlalchemy
    pip install plotly
    pip install pyvis
    pip install gunicorn
    ```

3. Run the following commands in the project's `app` directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        * `python data/process_data.py data/disaster_messages.csv data/disaster_categories.csv data/DisasterResponse.db`
    - To run ML pipeline that trains classifier and saves
        * `python run.py` 
        * (this will take approximately 30 minutes)
        * (I had to modify this, because of this issue: https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html)

4. Run the following command in the app's directory to run your web app.
    `gunicorn --bind 0.0.0.0:5000 wsgi:app`

5. Go to http://0.0.0.0:5000/disasterresponse