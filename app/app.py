# -*- coding: utf-8 -*-

import pathlib
import re
import json
from datetime import datetime
import flask
import dash
import dash_table
import matplotlib.colors as mcolors
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
import random
from dash.dependencies import Output, Input, State
from dateutil import relativedelta
from app.plotlywordcloud import plotly_wordcloud
from app.recommendengine import Recommender


### STATIC DATA PATHS ###
DATA_PATH = pathlib.Path(__file__).parent.resolve()
EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
USER_INTERACTIONS_CSV = "data/user-item-interactions.csv"
USER_ITEM_MATRIX_P = "data/user_item_matrix.p"
UDACITY_LOGO = "https://cdn.worldvectorlogo.com/logos/udacity.svg"


### Init Recommender Class ###
reco = Recommender(df_path=DATA_PATH.joinpath(USER_INTERACTIONS_CSV), 
                   matrix_path=DATA_PATH.joinpath(USER_ITEM_MATRIX_P))

### Get Lists for Dropdowns ###
USERS = reco.ra.get_all_users()
ARTICLES = reco.ra.get_all_articles()
TITLES = reco.ra.get_all_articles_titles()

### Fill List of Dicts for Dropdowns ###
user_labels = []
for user in USERS:
    user_labels.append(  {"label": user,
                          "value": user,
})
    
user_labels.append({"label": "New", "value": "new"})


article_labels = []
for article, title in zip(ARTICLES, TITLES):
    article_labels.append(  {"label": str(article)+": "+title,
                             "value": article,
})

    
### Load example images for article preview thumbnails
example_images = ["/static_recommendations/images/{}".format(x) for x in os.listdir("app/static/images")]


### Functions for populating the dicts from the RecommenderEngine into the Article Recommendations

def get_art_con(title, popularity=-1, similarity=-1):
    '''
    Create article within dash_bootstrap_components card html object.
    For now we're using random example images to draw the article preview.
    
    INPUT:
        title - (str) article title
        popularity - (int or float) single value that represents popularity of an article
        similarity - (int or float) single value that represents similiarity of an article
        
    OUTPUT:
        card - (object) dash_bootstrap_components HTML object
    '''
    
    if (popularity!=-1) and (similarity!=-1):
        badge_list = [dbc.Badge("Popularity: "+str(popularity), color="light", className="mr-1"),
                      dbc.Badge("Similarity: "+str(similarity), color="light", className="mr-1")]
    elif (similarity!=-1):
        badge_list = [dbc.Badge("Similarity: "+str(similarity), color="light", className="mr-1")]
    elif (popularity!=-1):
        badge_list = [dbc.Badge("Popularity: "+str(popularity), color="light", className="mr-1")]
    else:
        badge_list = [dbc.Badge("Similarity: "+str(similarity), color="light", className="mr-1 invisible")]
    
    card = dbc.Card([
            dbc.CardImg(src=random.choice(example_images), top=True),
            dbc.CardBody(
            [
                html.P(
                    title,
                    className="card-text",
                ),
                dbc.Col(children=[
                    dbc.Row(children=badge_list, style={"margin-bottom": 5}),
                    dbc.Row(dbc.Button("Read Article (dummy)", color="info", size="sm", style={"font-size": "0.8em"}))
                ])
            ])
    ], style={"height":"290px"})
    
    return card


def populate_reco_articles(art_dict_list):
    '''
    Will put the single articles into a grid of dash_bootstrap_components rows and columns.
    
    INPUT:
        art_dict_list - (list of dicts) every dict holds the keys "title", "popularity" and "similiarity"
    
    OUTPUT:
        body - (object) dash_bootstrap_components object that holds article grid ready for webapp
    '''
    
    row_children = []
    body = []
    for index, item in enumerate(art_dict_list):
        row_children.append(dbc.Col(
            get_art_con(item.get("title",""), 
                        item.get("popularity",-1),
                        item.get("similarity", -1))
            ))
        if ((index+1) % 3 == 0) and (index!=0):
            body.append(dbc.Row(children=row_children, 
                                style={"margin-bottom":8}))
            row_children = []
            
    for i in range(len(row_children),3):
        row_children.append(dbc.Col())
        
    body.append(dbc.Row(children=row_children,
                        style={"margin-bottom":8}))
    return body
        

def populate_table(df, n=10):
    '''
    Will convert an DataFrame into the suitable format for viewing inside an Dash DataTable.
    
    INPUT:
        df - (DataFrame) holds at least the columns "neighbor_id", "num_interactions" and "similarity"
        n - (int) Number of DataFrame rows to view in DataTable
    
    OUTPUT:
        columns - (list of dicts) holds the necessary info for every column for DataTable view
        data - (dict) represents DataFrame data in a dict
    '''
    
    
    df = df.iloc[1:11,:]
    df.rename(columns={"neighbor_id":"User ID", "num_interactions":"Activity", "similarity":"Similarity"}, inplace=True)
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')
    
    return columns, data
    

    
### Create Layout ###

# NAVBAR always on top of website
NAVBAR = dbc.Navbar(
    children=[
       
            dbc.Row(
                [
                    dbc.Col(html.A(html.Img(src=UDACITY_LOGO, height="20px"), href="https://www.udacity.com")),
                    dbc.Col(dbc.NavbarBrand("Recommendations with IBM Project"), className="ml-2"),
                    dbc.Col(dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("LinkedIn",
                                        href="https://www.linkedin.com/in/davidlassig/"),
                            dbc.DropdownMenuItem("Github Repo", 
                                        href="https://github.com/herrfeder/Udacity-Project-Recommendations-With-IBM-Webapp.git"),
                          
                        ],
                        nav=False,
                        in_navbar=True,
                        label="by David Lassig",
                        style={"color": "white", "font-size": 10, "font-weight":"lighter"},
                    )),
                    

                ],
                align="center",
                no_gutters=True,
            ),
           
        
    ],
    color="dark",
    dark=True,
    sticky="top",
)


LEFT_USER_COLUMN = dbc.Jumbotron(
    [
        html.H4(children="User Selection", className="display-5"),
        html.Hr(className="my-2"),

        html.Label("Select a User", style={"marginTop": 50}, className="lead"),
        html.P(
            "(Choose a user)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Dropdown(
            options=user_labels,
            value="new",
            id="user-drop", 
            clearable=False, 
            style={"marginBottom": 10, "font-size": 12}
        ),
        
        html.Label("Select Type of Recommendation", style={"marginTop": 50}, className="lead"),
        html.P(
            "(You have to change the user from new first for getting any result here)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Dropdown(
            options=[{"label":"Collaborative Filtering",
                      "value":"collab"},
                     {"label":"Singular Value Decomposition (SVD)",
                      "value":"svd"}
            ],        
            value="collab",
            id="reco-drop-user", 
            clearable=False, 
            style={"marginBottom": 30, "font-size": 12}
        ),
        
        
        html.Label("Select number of recommendations.", className="lead"),
        dcc.Slider(
            id="recommend-number-user",
            min=1,
            max=100,
            step=1,
            marks={
                10: "10",
                20: "",
                30: "30",
                40: "",
                50: "50",
                60: "",
                70: "70",
                80: "",
                90: "90",
                100: "",
            },
            value=10,
        ),
      
    ]
)

LEFT_ARTICLE_COLUMN = dbc.Jumbotron(
    [
        html.H4(children="Article Selection", className="display-5"),
        html.Hr(className="my-2"),

        html.Label("Select a Article", style={"marginTop": 50}, className="lead"),
        html.P(
            "(Will return articles with highest similarity)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Dropdown(
            options=article_labels,
            value=article_labels[0]["value"],
            id="article-drop", 
            clearable=False, 
            style={"marginBottom": 10, "font-size": 12}
        ),
        html.Label("Select Type of Recommendation", style={"marginTop": 50}, className="lead"),
        html.P(
            "(For articles we only have content based recommendation)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Dropdown(
            options=[{"label":"Content Based",
                      "value":"content"},
            ],        
            value="content",
            id="reco-drop-art", 
            clearable=False, 
            style={"marginBottom": 30, "font-size": 12}
        ),
        
        
        html.Label("Select number of recommendations.", className="lead"),
        dcc.Slider(
            id="recommend-number-art",
            min=1,
            max=100,
            step=1,
            marks={
                10: "10",
                20: "",
                30: "30",
                40: "",
                50: "50",
                60: "",
                70: "70",
                80: "",
                90: "90",
                100: "",
            },
            value=10,
        ),
      
    ]
)

    
RECOMMENDATIONS_USER = [
    dbc.CardHeader(html.H5("10 Best Recommendations for User New (Popularity Based)", id="reco-title-user")),
    dcc.Loading( id="loading-rec-user", children=[
        dbc.CardBody(children=[], id="reco-body-user", style={"overflow-y": "scroll", "height": "580px"} )])
]

RECOMMENDATIONS_ARTICLE = [
    dbc.CardHeader(html.H5("", id="reco-title-art")),
    dcc.Loading( id="loading-rec-art", children=[
        dbc.CardBody(children=[], id="reco-body-art", style={"overflow-y": "scroll", "height": "580px"} )])
]

WORDCLOUD_PLOT_USER = [
    dbc.CardHeader(html.H5("Most frequently tokenized words in user recommendation")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert-user",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [dbc.Col(
                        [ dcc.Loading( id="loading-wordcloud-user",
                                       children=[ dcc.Graph(id="userwordcloud-user")
                                                ], type="default",
                                     )
                        ]),
                 ])
         ]),
]


WORDCLOUD_PLOT_ARTICLE = [
    dbc.CardHeader(html.H5("Most frequently tokenized words in user recommendation")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert-art",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [dbc.Col(
                        [ dcc.Loading( id="loading-wordcloud-art",
                                       children=[ dcc.Graph(id="userwordcloud-art")
                                                ], type="default",
                                     )
                        ]),
                 ])
         ]),
]


TABLE_VIEW = [dbc.CardHeader(html.H5("10 Most Similiar Users")),
              dbc.CardBody(dcc.Loading(dash_table.DataTable(id="usertableview")))
                ]

BODY = dbc.Container(
    [dcc.Tabs([
        dcc.Tab(label='Collaboration Based Recommendation', children=[
          
            dbc.Row(
                [
                    dbc.Col(LEFT_USER_COLUMN, md=4, align="center"),
                    dbc.Col(dbc.Card(RECOMMENDATIONS_USER), md=8),
                ],
                style={"marginTop": 30},
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Card(WORDCLOUD_PLOT_USER), width=8),
                    dbc.Col(dbc.Card(TABLE_VIEW), width=4),
                    
            ])]),
            
        dcc.Tab(label='Content Based Recommendation', children=[
            dbc.Row(
                [
                    dbc.Col(LEFT_ARTICLE_COLUMN, md=4, align="center"),
                    dbc.Col(dbc.Card(RECOMMENDATIONS_ARTICLE), md=8),
                ],
                style={"marginTop": 30},
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Card(WORDCLOUD_PLOT_ARTICLE)),
            ])
        ])
    ]),
], className="mt-12",)
        

### Init webapp ###


app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                url_base_pathname="/recommendations/",
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
                ],
               )

app.layout = html.Div(children=[NAVBAR, BODY])
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

server = app.server

### Callback for Collaborative Tab tableview, wordcloud and recommendations ###
@app.callback(
    [
        Output("userwordcloud-user", "figure"),
        Output("reco-body-user", "children"),
        Output("no-data-alert-user", "style"),
        Output("reco-title-user", "children"),
        Output("usertableview", "data"),
        Output("usertableview", "columns"),
    ],
    [
        Input("user-drop", "value"),
        Input("recommend-number-user", "value"),
        Input("reco-drop-user", "value")
    ],
)
def update_wordcloud_reco_user(user_id, rec_number, rec_type):
    """ Callback to rerender wordcloud plot """
    if user_id=="new":
        reco_title = "{} Best Recommendations for User {} (Article Popularity)".format(rec_number, user_id)
        user_recs, word_text, rec_ids = reco.ra.get_top_articles(rec_number)
        data=[]
        columns=[]
    else:
        if rec_type=="collab":
            reco_title = "{} Best Recommendations for User {} (Similarity of Users)".format(rec_number, user_id)
            user_recs, word_text, rec_ids, neighbors_df = reco.make_collab_recs(user_id, rec_number)
            columns, data = populate_table(neighbors_df)
        elif rec_type=="svd":
            reco_title = "{} Best Recommendations for User {} (Similarity of Users SVD)".format(rec_number, user_id)
            user_recs, word_text, rec_ids, neighbors_df = reco.make_collab_recs(user_id, base="pred", m=rec_number)
            columns, data = populate_table(neighbors_df)

    
    wordcloud = plotly_wordcloud(word_text)
    reco_body = populate_reco_articles(user_recs)
    alert_style = {"display": "none"}
    if (wordcloud == {}):
        alert_style = {"display": "block"}
    
    return (wordcloud, reco_body, alert_style, reco_title, data, columns)


### Callback for Content Tab tableview, wordcloud and recommendations ###
@app.callback(
    [
        Output("userwordcloud-art", "figure"),
        Output("reco-body-art", "children"),
        Output("no-data-alert-art", "style"),
        Output("reco-title-art", "children")
    ],
    [
        Input("article-drop", "value"),
        Input("recommend-number-art", "value"),
    ],
)
def update_wordcloud_reco_article(article_id, rec_number):
   
    reco_title = "{} Best Recommendations for Articles {} (Content Based)".format(rec_number, article_id)
    user_recs, word_text, rec_ids = reco.make_content_recs(article_id, rec_number)

    wordcloud = plotly_wordcloud(word_text)
    reco_body = populate_reco_articles(user_recs)
    alert_style = {"display": "none"}
    if (wordcloud == {}):
        alert_style = {"display": "block"}
    
    return (wordcloud, reco_body, alert_style, reco_title)




if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")