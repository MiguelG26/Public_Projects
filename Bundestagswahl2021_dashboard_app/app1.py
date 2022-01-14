import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import datetime
from datetime import date, timedelta
from dash.dependencies import Input, Output

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server# only for heroku

#To get the data
df = pd.read_excel('ergebnisse_2021_clean.xlsx')
'''
df = pd.read_excel('ergebnisse_2021.xlsx')
df=df[['Gebietsart', 'Gebietsname', 'Gruppenart', 'Gruppenname',
       'Stimme', 'Anzahl', 'Prozent', 'VorpAnzahl',
       'VorpProzent', 'DiffProzent', 'DiffProzentPkt', 'UegGebietsnummer', 'Gebietsnummer']]

#to get the sum CDU+CSU -> CDU/CSU
df_CDU=df[(df['Gruppenname']=="CDU")|(df['Gruppenname']=="CSU")].groupby(
    ['Gebietsart', 'Gebietsname', 'Gruppenart','Stimme']).sum()
df_CDU=df_CDU.reset_index()
df_CDU['Gruppenname']="CDU/CSU"
df_CDU=df_CDU[['Gebietsart', 'Gebietsname', 'Gruppenart', 'Gruppenname', 'Stimme',
       'Anzahl', 'Prozent', 'VorpAnzahl', 'VorpProzent', 'DiffProzent',
       'DiffProzentPkt','UegGebietsnummer', 'Gebietsnummer']]
df = df.append(df_CDU, ignore_index=True)

#to remove the CDU & CSU lines
indexNames = df[(df['Gruppenname'] =="CDU") | (df['Gruppenname'] =="CSU") ].index
df=df.drop(indexNames)
df['joker']=df['Gebietsname']+"_"+df['Gruppenart']+"_"+df['Stimme'].astype(str)

#to identify the winning parties
df['max']= df['Prozent']==df['joker'].apply(lambda y:df[df["joker"]==y].max()["Prozent"])
'''
gebietsart_options = [{'label': 'All', 'value': 'All'}]
for gebietsart in df['Gebietsart'].unique():
    gebietsart_options.append({'label':str(gebietsart),'value':gebietsart})
del gebietsart_options[0]

mymap={'CDU/CSU':'#004B76','SPD':'#C0003D','GRÜNE':'#008549','FDP':'#F7BC3D','AfD':'#80CDEC',
       'DIE LINKE':'#5F316E','Sonstige':'#BEC5C9'}

#######################################################################
#To create the bldf: BundeLänder DataFrame
bldf=df[df['Gebietsart']=='Land'].groupby(['Gebietsnummer','Gebietsname']).sum().reset_index()[['Gebietsnummer','Gebietsname']]
bldf = bldf.rename(columns={'Gebietsnummer': 'UegGebietsnummer'})

#To get the stbldf: SitzPlätze pro BundesLand DataFrame
stbldf=df[(df['Gebietsart']=='Wahlkreis')&(df['Gruppenart']=="Partei")&(df['Stimme']==1)][
    ['UegGebietsnummer', 'Gebietsnummer','Gruppenname','Anzahl','Prozent','max']]
stbldf=stbldf[stbldf['max']==True]

stbldf=stbldf.pivot_table(values='Anzahl',index=['UegGebietsnummer','Gruppenname'],aggfunc='count')
stbldf=stbldf.reset_index().sort_values(['UegGebietsnummer','Anzahl'], ascending=[True, False])

stbldf = pd.merge(stbldf, bldf)
stbldf=stbldf[['Gebietsname','Gruppenname','Anzahl']]

stbldf['Prozent']= stbldf['Anzahl']/stbldf['Gebietsname'].apply(lambda y:stbldf[stbldf["Gebietsname"]==y].sum()["Anzahl"])*100
stbldf['Prozent']=stbldf['Prozent'].round(2)
stbldf['max']= stbldf['Anzahl']==stbldf['Gebietsname'].apply(lambda y:stbldf[stbldf["Gebietsname"]==y].max()["Anzahl"])
#######################################################################

def data_sitzplaetze(gebietsname):
    if gebietsname == "Bundesgebiet":
        df0=stbldf.groupby(['Gruppenname'])['Anzahl'].sum().sort_values().reset_index()
        df0['Prozent']=(df0['Anzahl']/df0['Anzahl'].sum()*100).round(2)
        title= "Sitzplätze (Direktmandate) pro Partei Bundesweit"
    else:
        df0=stbldf[stbldf['Gebietsname']==gebietsname][['Gruppenname','Anzahl','Prozent']].sort_values(
            'Anzahl')
        title= "Sitzplätze (Direktmandate) pro Partei. Land: "+ gebietsname
    df1=df0.copy() # this is done to keep the very similar code as below
    df1['color']=df1['Gruppenname'].map(mymap)
    colors=list(df1['color'])
    return df1, colors

def data_wpbldf():
    #To get the stbldf: Winner Partei pro BundesLand DataFrame
    wpbldf=stbldf[stbldf['max']].sort_values('Gebietsname', ascending = False)[['Gebietsname','Gruppenname', 'Anzahl', 'Prozent']] #to display only the party with more setas per bundesland
    df1=wpbldf.copy() # this is done to keep the very similar code as below
    df1['color']=df1['Gruppenname'].map(mymap)
    colors=list(df1['color'])
    return df1, colors

def data_stimme(gebietsart, gebietsname, stimme):
    gruppenart = 'Partei'
    if gebietsart == "Bund":
        df0=df[(df['Gebietsart']==gebietsart)&(df['Gruppenart']==gruppenart)&(df['Stimme']==stimme)][
            ['Gruppenname','Anzahl','Prozent']].sort_values('Prozent',ascending=False).copy()
        title= "Bundestagswahl 2021: vorläufiges Ergebnis"
    elif gebietsart == "Land":
        df0=df[(df['Gebietsart']==gebietsart)&(df['Gruppenart']==gruppenart)&(df['Stimme']==stimme)&(df['Gebietsname']==gebietsname)][
            ['Gruppenname','Anzahl','Prozent']].sort_values('Prozent',ascending=False).copy()
        title= "Bundestagswahl 2021: vorläufiges Ergebnis. Land: "+ gebietsname
    elif gebietsart == "Wahlkreis":
        df0=df[(df['Gebietsart']==gebietsart)&(df['Gruppenart']==gruppenart)&(df['Stimme']==stimme)&(df['Gebietsname']==gebietsname)][
            ['Gruppenname','Anzahl','Prozent']].sort_values('Prozent',ascending=False).copy()
        title= "Bundestagswahl 2021: vorläufiges Ergebnis. Wahlkreis: "+ gebietsname

    df0['Anzahl_M']=df0['Anzahl']/1000000
    df0=df0[['Gruppenname','Anzahl','Anzahl_M','Prozent']]
    voters=df0['Anzahl'].sum()
    voters_M=df0['Anzahl_M'].sum()

    #to extract only the top 7 (or 8) parties
    if gebietsart == "Bund":
        df1=df0.head(7)#.sort_values('Prozent')
        df1 = df1.append(df0[df0['Gruppenname']=='SSW'], ignore_index=True).sort_values('Prozent')
        ind_sons=0

        #To change te order of the last 2 rows
        row0=df1.iloc[0]
        row1=df1.iloc[1]
        df1.iloc[0]=row1
        df1.iloc[1]=row0
    else:
        df1=df0.head(7).sort_values('Prozent')
        ind_sons=0

    df1["Gruppenname"].iloc[ind_sons]='Sonstige'
    df1['Anzahl'].iloc[ind_sons]=voters-df1['Anzahl'].sum()+df1['Anzahl'].iloc[ind_sons]
    df1['Anzahl_M'].iloc[ind_sons]=voters_M-df1['Anzahl_M'].sum()+df1['Anzahl_M'].iloc[ind_sons]
    df1['Prozent'].iloc[ind_sons]=100-df1['Prozent'].sum()+df1['Prozent'].iloc[ind_sons]

    df1['Prozent']=round(df1['Prozent'],2)
    df1['Anzahl_M']=round(df1['Anzahl_M'],2)

    df1['color']=df1['Gruppenname'].map(mymap)
    colors=list(df1['color'])
    return df1, colors

rectangle = html.Div([
        html.Br([]),
        html.Div([
                html.P(
                    "Dieses Dashboard der Bundestagswahlen 2021 in Deutschland wurde ausschließlich in Phyton \
                    mit der Dash Library von Plotly und ganz viel Liebe ♡ erstellt",
                    style={"color": "#ffffff",'fontSize': 15},
                    className="row",
                )
            ],className="product",)
    ],style={'width':'100%','display':'inline-block'})

filters=html.Div([
        html.Br([]),
        html.Div([
            html.Div([html.H5('Gebietsart auswählen:', style= {'color':'#959a99','font-weight':"bold"})],className="three columns"),
            html.Div([html.H5('Gebietsname auswählen:', style= {'color':'#959a99','font-weight':"bold", 'float': 'left'})],className="three columns"),
            html.Div([html.H6('', style= {'color':'#959a99','font-weight':"bold", 'float': 'left', 'padding-left': '40px'})],className="six columns"),
            ],className="row"),
        html.Div([
                html.Div([#content deleted
                    ],className="three columns" ),
                html.Div([#content deleted
                    ],className="three columns" ),
                html.Div([
                    html.P(
                    dcc.Dropdown(id='Gebietsart_picker',options=gebietsart_options,value='Bund'),
                    style= {'padding-right': '60px', 'font-size': '15px'}
                    ),
                    ],className="three columns"),

                html.Div([
                    html.P(
                    dcc.Dropdown(id='Gebietsname_picker', value="Bundesgebiet"),
                    style= {'padding-right': '60px', 'font-size': '15px'}
                    ),
                    ],className="three columns"),
            ],style={'width':'100%','display':'inline-block', 'background': '#ffffff'}),
    ])

header = html.Div([
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("Ergebnisse der Bundestagswahl 2021", style= {'display': 'flex','align-items': 'right'}),
                        ],className="twelve columns main-title",
                    )
                ],style={'width':'100%','display':'inline-block'}
            ),
            rectangle,
            filters,
    ],className="header_bar",
)

body=html.Div([
        #row 1
        html.Div([
            html.Div([
                    html.Div(dcc.Graph(id='Gr_1_stimme'), className="six columns",),
                    html.Div(dcc.Graph(id='Gr_2_stimme'), className="six columns",),
                ],className="twelve columns",)
            ],className="row"),

        #row 2
        html.Div([
            html.Div([
                    html.Div(dcc.Graph(id='Gr_sitzplaetze'), className="six columns", style= {'display': 'block'}),
                    html.Div(dcc.Graph(id='Gr_sitzplaetze2'), className="six columns", style= {'display': 'block'}),
                    #html.Div(dcc.Graph(id='Gr_2_stimme'), className="six columns",),
                ],className="twelve columns",)
            ],className="row"),

        html.Div([
            html.Br([]),
            html.Div([
                    html.P(
                        "Quelle: https://www.bundeswahlleiter.de/bundestagswahlen/2021/ergebnisse/opendata/csv/kerg2.csv",
                        style={"color": "#ffffff",'fontSize': 12},
                        className="row",
                    )
            ],className="product",)
    ],style={'width':'100%','display':'inline-block'})

    ],className="cuerpo",)


app.layout = html.Div([body,header],className="page")

#"""
#  Callbacks
#"""

#####Gebietsname_picker
@app.callback(
    Output('Gebietsname_picker', 'options'),
    [Input('Gebietsart_picker', 'value')])
def upd_Gebietsname_picker(gebietsart):
    gebietsname_options = [{'label': 'All', 'value': 'All'}]
    for gebietsname in sorted(df['Gebietsname'][df['Gebietsart']==gebietsart].unique()):
        gebietsname_options.append({'label':str(gebietsname),'value':gebietsname})
    del gebietsname_options[0]

    return gebietsname_options

@app.callback(
    Output('Gebietsname_picker', 'value'),
    [Input('Gebietsart_picker', 'value')])
def upd_Gebietsname_picker(gebietsart):
    if gebietsart== "Bund":
        start_value="Bundesgebiet"
    elif gebietsart== "Land":
        start_value="Baden-Württemberg"
    elif gebietsart== "Wahlkreis":
        start_value="Stuttgart I"
    return start_value

#####Charts
#row1
@app.callback(
    Output('Gr_1_stimme', 'figure'),
    [Input('Gebietsart_picker', 'value'),
     Input('Gebietsname_picker', 'value')])
def upd_Gr_1_stimme(gebietsart, gebietsname, stimme=1):
    df1, colors=data_stimme(gebietsart, gebietsname, stimme)

    return {
        'data':[
            go.Bar(y=df1['Gruppenname'] +"  ", x=df1['Prozent'],
           text=df1['Anzahl_M'].astype(str)+" Mio. Stimmen | "+ df1['Prozent'].astype(str) +"%",orientation="h",
           marker_color=colors, textposition='auto',),
        ],
        'layout':go.Layout(template="simple_white", showlegend=False,
                  title ={'text': '<b>1. Stimme</b>'+ '<br> '},
                  xaxis =dict(showticklabels=False,showline=False,ticks='' ),
                  yaxis =dict(showline=False, zeroline = False,ticks=''),
                    )
    }

@app.callback(
    Output('Gr_2_stimme', 'figure'),
    [Input('Gebietsart_picker', 'value'),
     Input('Gebietsname_picker', 'value')])
def upd_Gr_2_stimme(gebietsart, gebietsname, stimme=2):
    df1, colors=data_stimme(gebietsart, gebietsname, stimme)
    return {
        'data':[
            go.Bar(y=df1['Gruppenname'] +"  ", x=df1['Prozent'],
           text=df1['Anzahl_M'].astype(str)+" Mio. Stimmen | "+ df1['Prozent'].astype(str) +"%",orientation="h",
           marker_color=colors,textposition='auto',),
        ],
        'layout':go.Layout(template="simple_white",
                  title ={'text': '<b>2. Stimme</b>'+ '<br> '},
                  xaxis =dict(showticklabels=False,showline=False,ticks='' ),
                  yaxis =dict(showline=False, zeroline = False,ticks=''),
                    )
    }

#row2
@app.callback(
    Output('Gr_sitzplaetze', 'figure'),
    [Input('Gebietsname_picker', 'value')])
def upd_Gr_sitzplaetze(gebietsname):
    df1, colors=data_sitzplaetze(gebietsname)
    return {
        'data':[
            go.Bar(y=df1['Gruppenname'] +"  ", x=df1['Prozent'],
           text=df1['Anzahl'].astype(str)+" Sitzplätze | "+ df1['Prozent'].astype(str) +"%",orientation="h",
           marker_color=colors,textposition='auto',),
        ],
        'layout':go.Layout(template="simple_white",
                  title ={'text': '<b>Sitzplätze (Direktmandate) pro Partei</b>'+ '<br> '},
                  xaxis =dict(showticklabels=False,showline=False,ticks='' ),
                  yaxis =dict(showline=False, zeroline = False,ticks=''),
                    )
    }

@app.callback(
    Output('Gr_sitzplaetze2', 'figure'),
    [Input('Gebietsname_picker', 'value')])
def upd_Gr_sitzplaetze2(gebietsname):
    df1, colors=data_wpbldf()
    return {
        'data':[
            go.Bar(y=df1['Gebietsname'] +"  ", x=df1['Prozent'],
           text=df1['Gruppenname'].astype(str)+" | " + df1['Anzahl'].astype(str)+" Sitzplätze | "+ df1['Prozent'].astype(str) +"%",orientation="h",
           marker_color=colors,textposition='auto',),
        ],
        'layout':go.Layout(template="simple_white", height=600,
                  title ={'text': '<b>Partei mit dem meisten Sitzplätze (Direktmandate) pro Bundesland</b>'+ '<br> '},
                  xaxis =dict(showticklabels=False,showline=False,ticks='' ),
                  yaxis =dict(showline=False, zeroline = False,ticks=''),
                    )
    }

#show_hide_elements
@app.callback(
    Output('Gr_sitzplaetze2', 'style'),
    [Input('Gebietsart_picker', 'value')])
def show_hide_sitzplaetze2(Gebietsart):
    if Gebietsart == "Bund":
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('Gr_sitzplaetze', 'style'),
    [Input('Gebietsart_picker', 'value')])
def show_hide_sitzplaetze1(Gebietsart):
    if Gebietsart == "Wahlkreis":
        return {'display': 'none'}
    else:
        return {'display': 'block'}

# Add the server clause:
if __name__ == '__main__':
    app.run_server(debug=True)
