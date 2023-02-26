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
            # st.write(self.location)
            if platform.system() == 'Darwin':
                st.markdown(f"[{self.location}](https://maps.apple.com/?q='{urllib.parse.quote(self.location)}')",unsafe_allow_html=True)
            else:
                st.markdown(f"[{self.location}](https://maps.google.com/?q='{urllib.parse.quote(self.location)}')",unsafe_allow_html=True)

        if self.description:
            st.markdown(self.remove_span(self.description),unsafe_allow_html=True)
        st.markdown("---")


st.cache_data(ttl=3600) # 1 hour
def get_data(credentials, maxresults):
    service = build('calendar', 'v3', credentials=credentials)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='73976030d4b82ca7595f9194853a0693015e1b7c3830133cacf67ac0f153e04b@group.calendar.google.com', timeMin=now,
                                              maxResults=maxresults, singleEvents=True,
                                              orderBy='startTime').execute()

    return events_result.get('items', [])



if __name__ == "__main__":
    st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")

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


