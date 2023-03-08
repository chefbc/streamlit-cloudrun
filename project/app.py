import streamlit as st
import pandas as pd
import numpy as np

import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import datetime, timedelta

import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
# from rich import inspect

from dataclasses import dataclass
from jinja2 import Template
from os.path import exists

from googleapiclient.discovery import build

import re

import datetime
import platform
import urllib

from user_agents import parse

# st.cache_data(ttl=3600)

@dataclass
class GoogleCalendarEvent:
    """Class for GoogleCalendarEvent"""
    # event: dict

    summary: str
    location: str
    description: str
    start_date: str
    end_date: str

    def remove_span(self, html_string):
        return re.sub(r'<span.*?>(.*?)</span>', r'\1', html_string)

    def replace_br_with_newline(self, html_string):
        """Replace <br /> tags with newline characters"""
        return re.sub(r'<br\s*/?>', '\n', html_string)

    def _suffix(self, d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

    def _datetime_format(self, value: str, format="%H:%M %d-%m-%y"):
        date_obj = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        
        #st.write(date_obj)

        x = date_obj.strftime(format).replace('{S}', str(date_obj.day) + self._suffix(date_obj.day))
        #st.write(x)
        return x

    def display(self):
        st.write("")
        st.header(self.summary)
        st.caption(self._datetime_format(self.start_date, '%A, %B {S}  %-I:%M %p'))
        if self.location:            
            #st.markdown(f"{locate_name} {apple_maps} {google_maps}",unsafe_allow_html=True)
            st.write(self.location.split(',')[0])
            st.markdown('<ul style="list-style-type: none;">',unsafe_allow_html=True)
            st.markdown('<li style="list-style-type: none;"><a href="https://maps.apple.com/?q=\'{urllib.parse.quote(self.location)}\'"><i class="fa-brands fa-apple" style="margin: 0 1em 0 0;"></i>Apple Maps</a></li>', unsafe_allow_html=True)
            st.markdown('<li style="list-style-type: none;"><a href="https://maps.goolge.com/?q=\'{urllib.parse.quote(self.location)}\'"><i class="fa-brands fa-google" style="margin: 0 1em 0 0;"></i>Google Maps</a></li>', unsafe_allow_html=True)
            st.markdown('</ul>',unsafe_allow_html=True)

        if self.description:

            content = self.description.split("---")

            cols = st.columns(len(content))

            for idx, md in enumerate(content):
                # st.write(idx)
                # st.write(md)
                md = self.remove_span(md)
                md = self.replace_br_with_newline(md)
                cols[idx].markdown(md, unsafe_allow_html=True)

            # st.markdown(self.remove_span(self.description),unsafe_allow_html=True)

        st.markdown("---")


st.cache_data(ttl=3600) # 1 hour
def get_data(credentials, maxresults):
    service = build('calendar', 'v3', credentials=credentials)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='73976030d4b82ca7595f9194853a0693015e1b7c3830133cacf67ac0f153e04b@group.calendar.google.com', timeMin=now,
                                              maxResults=maxresults, singleEvents=True,
                                              orderBy='startTime').execute()

    return events_result.get('items', [])

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def fa():
    ### Font Awesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css">', unsafe_allow_html=True)



if __name__ == "__main__":
    st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
    local_css("./static/streamlit.css")
    fa()

    # st.write(platform.system())
    # st.write(user_agent.os.family)

    query_params = st.experimental_get_query_params()

    maxresults = query_params.get('max', ["nodigit"])[0]

    maxresults = int(maxresults) if maxresults.isdigit() else 10

    st.title("📅 Latest Events")
    st.markdown("---")

    # auth
    key_path = st.secrets.get("key_path", "")

    scopes = ['https://www.googleapis.com/auth/calendar.readonly']

    if exists(key_path):
        credentials = service_account.Credentials.from_service_account_file(
          key_path, scopes=scopes,
      )
    else:
        credentials, _ = google.auth.default(scopes=scopes)
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
 
    # service = build('calendar', 'v3', credentials=credentials)

    events = get_data(credentials, maxresults)
    # st.write(events)

    for event in events:
        # st.write(event)
        cal_entry = GoogleCalendarEvent(
            summary=event.get('summary'),
            location=event.get('location', None),
            description=event.get('description', None),
            start_date=event['start'].get('dateTime', event['start'].get('date')),
            end_date=event['end'].get('dateTime', event['end'].get('date'))
        )

        # st.write(cal_entry)
        cal_entry.display()


