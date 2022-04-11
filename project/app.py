from pyparsing import one_of
import streamlit as st
import pandas as pd
import numpy as np

from st_aggrid import AgGrid

import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
# from datetime import datetime
from datetime import datetime, timedelta

st.title('KM Pole Vault Page')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data['date'] = pd.to_datetime(data['DATE_COLUMN'])
    # df3['date']= pd.to_datetime(df3['date'])

    return data

@st.cache
def load_sheet(sheet: gspread.spreadsheet.Spreadsheet, tab_name: str) -> pd.DataFrame:
    tab = sheet.worksheet(tab_name)
    # df1.drop(df1[df1['date'].isnull()].index, inplace=True)
    df = get_as_dataframe(tab, parse_dates=True, usecols=[*range(0, 10)]) #.fillna('')
    df.drop(df[df['date'].isnull()].index, inplace=True)
    df['date']= pd.to_datetime(df['date'])
    df['time'] = df['time'].fillna(pd.to_datetime('2022-01-01'))
    df['time']= pd.to_datetime(df['time'])

    return df.fillna('')


# data_load_state = st.text('Loading data...')
# data = load_data(10000)
# data_load_state.text("Done! (using st.cache)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def attempt(name, school, school_year) -> None:

    with st.form(f"{name}_{school}_attempt"):
        #st.title(name)
        #st.caption(f'{school} | {school_year}')
        
        head1, head2, = st.columns([6, 1])

        with head1:
            st.title(name)
            st.caption(f'{school} | {school_year}')

        with head2:
            st.title(f"feet-inches")
        

        attempt1, attempt2, attempt3 = st.columns(3)
        
        with attempt1:
            option1 = st.selectbox(
                'Attempt 1',
                ('.', 'Pass', 'Make', 'Miss'),
                key='option1',
                disabled=False,
            )
            # st.write(option1)
        
        with attempt2:
            option2 = st.selectbox(
                'Attempt 2',
                ('.', 'Pass', 'Make', 'Miss'),
                key='option2',
                disabled=(False if option1 == 'Miss' else True)
            )

        with attempt3:
            option3 = st.selectbox(
                'Attempt 3',
                ('.', 'Pass', 'Make', 'Miss'),
                key='option3',
                disabled=(False if option2 == 'Miss' else True)
            )
        
        submitted = st.form_submit_button("Save")
        if submitted:
            st.write('You selected:', f"{option1}, {option2}, {option3}")



def format_row(row) -> str:
    return f"""
    {row['name'].title()}  
    @{row['location'].title()} 
    {row['date'].strftime('%a, %B %d %Y')} 
    {row['time'].strftime('%I:%M %p')}
    """


if __name__ == "__main__":
    # active_tab = tabs(["Tab 1", "Tab 2", "Tab 3"])
    local_css("/usr/src/app/project/static/streamlit.css")

    #attempt("Hulk Hogan", "Kettle Moraine", "10th")
    #attempt("Macho Man Randy Savage", "Waukesha North", "12th")

    #df = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv')
    #AgGrid(df)

    gc = gspread.service_account(filename='/usr/src/app/project/chefbc-cd4d1fb4ed74.json')

    #st.write(gc.list_spreadsheet_files())

    google_sheet = gc.open('PVStreamlit')

    events = load_sheet(google_sheet, 'Events')
    meets = load_sheet(google_sheet, 'Meets')

    df3 = pd.concat([events, meets])
    df3.reset_index(drop=True)

    #all = 
    # st.write(all.loc[all['date'] >= '2022-05-01 00:58:10'])
    # df4 = df3.loc[df3['date'] >= '2022-05-01 00:58:10'] 
    
    # timedelta(-1)
    #today = datetime.now().timedelta(-1)
    #yesterday = timedelta(-1)
    #st.write
    
    df4 = df3.loc[df3['date'] >= datetime.today() - timedelta(days = 1)]

    df4.sort_values(by=['date'], ascending=[True], inplace=True)
    # df4.reset_index(drop=True)
    # df4.reset_index(drop=True, inplace=True)
    # reindex?


    # st.write(df4)
    # st.expander(label, expanded=False)

    # Step: Keep rows where date >= 2020-04-01 00:58:10
    
    #df4 = df3.loc[df3['date'] >= datetime.now()]

    #for row in all.iterrows():
    for idx, row in df4.iterrows():

        # st.write(row['name'])
        # st.write(format_row(row))
        #st.write(type(row))
        # if idx <= 5
        # st.write(idx)
        # with st.expander(format_row(row), expanded=idx <= 5):
        #     st.write(row['description'])


        # with st.container():
        #     st.write(format_row(row))
        #     st.write(row['description'])
        with st.form(f"{row['type']}{idx}"):
            # st.write(f"{row['type']}{idx}")

            head1, head2, = st.columns([3, 1])

            with head1:
                st.markdown(f"#### {row['name']}") # @ {row['location']}")
                st.markdown(f"###### @ {row['location']}")
                st.caption(f"Team: {row['gender']}")
                st.caption(f"Level: {row['team']}")

            with head2:
                # st.title(f"feet-inches")
                st.markdown(f"###### {row['date'].strftime('%a, %B %d %Y')}")
                st.markdown(f"###### {row['time'].strftime('%-I:%M %p')}")

            #st.markdown(f"#### {row['name']}")
            #st.markdown(f"###### {row['location']}")

            #st.subheader(row['date'].strftime('%a, %B %d %Y'))
            #st.caption(row['time'].strftime('%I:%M %p'))
            st.write(row['description'])

            submitted = st.form_submit_button("Save")
            if submitted:
                st.write('You selected:', f"clicked")

        

    # st.write(all.sort_values(by=['date'], ascending=[True]))

    # AgGrid(all.sort_values(by=['date'], ascending=[True]))


   # st.write(load_sheet(google_sheet, 'Events'))

   # st.write(load_sheet(google_sheet, 'Meets'))
