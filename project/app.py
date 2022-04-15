import streamlit as st
import pandas as pd
import numpy as np

import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime, timedelta

import google.auth
import google.auth.transport.requests
# from rich import inspect

from dataclasses import dataclass
from jinja2 import Template
from os.path import exists

@st.cache
def load_sheet(sheet: gspread.spreadsheet.Spreadsheet, tab_name: str) -> pd.DataFrame:
    tab = sheet.worksheet(tab_name)
    # df1.drop(df1[df1['date'].isnull()].index, inplace=True)
    df = get_as_dataframe(tab, parse_dates=True, usecols=[*range(0, 11)]) #.fillna('')
    df.drop(df[df['date'].isnull()].index, inplace=True)
    
    df['bus']= pd.to_datetime(df['bus'])
    df['bus'] = df['bus'].fillna(pd.to_datetime('2022-01-01'))
    # df['bus'] = df['bus'].fillna('DATE')

    df['who'] = df['who'].fillna('ALL')
    # df['info'] = df['info'].fillna('-')

    df['date']= pd.to_datetime(df['date'])

    df['time'] = df['time'].fillna(pd.to_datetime('2022-01-01'))
    df['time']= pd.to_datetime(df['time'])

    return df.fillna('')


@st.cache
def get_events(gc, sheet_name: str, tabs: list) -> pd.DataFrame:
    
    google_sheet = gc.open('PVStreamlit')

    events = load_sheet(google_sheet, 'Events')
    meets = load_sheet(google_sheet, 'Meets')

    df3 = pd.concat([events, meets])
    df3.reset_index(drop=True)
    
    df4 = df3.loc[df3['date'] >= datetime.today() - timedelta(days = 1)]

    df4 = df4.sort_values(by=['date'], ascending=[True])#, inplace=True)
    # # df4.reset_index(drop=True)
    # df4.reset_index(drop=True, inplace=True)

    return df4

@dataclass
class EventItem:
    """Class for event."""
    name: str
    location: str
    bus: datetime
    time: datetime
    date: datetime
    event_type: str 
    #team: str 
    #gender: str
    who: str
    info: str
    link: str

    t = Template('''
        <article class="card fl-left">
            <section class="date">
                <time>
                    <span>{{ date.strftime('%-d') }}</span>
                    <span>{{ date.strftime('%b') }}</span>
                </time>
            </section>
            <section class="card-cont">
                <small>{{event_type}}</small>
                <h3>{{name}}</h3>
                <div class="even-date">
                    <i class="fa fa-calendar"></i>
                    <time>
                        <span>{{ date.strftime('%A, %B %-d %Y') }}</span>
                        <span>{{time_string}}</span>
                    </time>
                </div>
                <div class="even-info">
                    <i class="fa fa-user"></i>
                    <p>{{who}}</p>
                </div>
                <div class="even-info">
                    <i class="fa fa-info"></i>
                    <p>{{info}}</p>
                </div>
                <div class="even-info">
                    <i class="fa fa-map-marker"></i>
                    <p>{{location}}</p>
                    {% if event_type == 'meet2' -%}
                        <a href="#" class="button">Details</a>
                    {% endif -%}
                </div>
            </section>
        </article>''')

    def render_html(self) -> str:
        return self.t.render(
            event_type=self.event_type,
            name=self.name, 
            date=self.date,
            # bus=None if self.bus == pd.Timestamp('2022-01-01') else self.bus,
            #time=None if self.time == pd.Timestamp('2022-01-01') else self.time,
            time_string=self.__format_time(self.bus, self.time),
            who=self.who,
            info=self.info,
            location=self.location,
            link=self.link,
            )

    def __format_time(self, bus: pd.Timestamp, time: pd.Timestamp,) -> str:
        if bus == pd.Timestamp('2022-01-01'):
            b = ''
        else:
            b =  f"Bus: {bus.strftime('%-I:%M %p')}"

        if time == pd.Timestamp('2022-01-01'):
            t = '&nbsp;'
        else:
            t = f"Time: {time.strftime('%-I:%M %p')}"

        return f"{b}   {t}"




def event_df_to_list(df: pd.DataFrame) -> list:
    # st.write(df.head())
    x = []
    for date in df['date'].unique():
        df2 = df.loc[df['date'] == date] 
        t = []
        for idx, row in df2.iterrows():
            t.append(
                EventItem(
                    name=row['name'], 
                    location=row['location'], 
                    bus=row['bus'],
                    time=row['time'],
                    date=row['date'], 
                    event_type= row['type'],
                    #row['team'],
                    #row['gender'],
                    who=row['who'],
                    info=row['info'],
                    link=row['link'],
                )
            )      
        x.append(t)
    return x

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def fa():
    ### Font Awesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)

def format_row(row) -> str:
    return f"""
    {row['name'].title()}  
    @{row['location'].title()} 
    {row['date'].strftime('%a, %B %d %Y')} 
    {row['time'].strftime('%I:%M %p')}
    """

def html(event_list, weight_sheet_url) -> str:
    x = []
    x.append(f'<section class="container">\n')
    x.append(f'     <h1>Pole Vault gigs</h1>\n')
    x.append(f'         <a href="{weight_sheet_url}" target="_blank" rel="noopener noreferrer">Weight Sheet</a>\n')

    x.append(f'     <section class="container">\n')
    
    for e in event_list:
        x.append(f'     <div class="row">')
        for item in e:
            x.append(f'{item.render_html()}')
        x.append(f'\n     </div>\n')
    x.append(f'</section>')

    return ''.join(x)

if __name__ == "__main__":
    st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
    local_css("/usr/src/app/project/static/cal3.css")
    fa()

    # auth
    if exists('/usr/src/app/project/chefbc-cd4d1fb4ed74.json'):
        gc = gspread.service_account(filename='/usr/src/app/project/chefbc-cd4d1fb4ed74.json')
    else:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials, _ = google.auth.default(scopes=scopes)
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        gc = gspread.authorize(credentials)


    events_df = get_events(gc,'PVStreamlit', [])

    event_list = event_df_to_list(events_df)

    # weight sheet
    if datetime.today() > datetime(2022, 5, 16):
        weight_sheet_url = "https://drive.google.com/file/d/1J3asehXra0R7ZIIQWswgSDn4sR3h7oES/view?usp=sharing"
    else:
        weight_sheet_url = "https://drive.google.com/file/d/1fukftB9zKPpQvcuLi3Cca2FX6GA8UDE5/view?usp=sharing"


    st.markdown(html(event_list, weight_sheet_url), unsafe_allow_html=True)
