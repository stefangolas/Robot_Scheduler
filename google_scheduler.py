# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 17:09:10 2022

@author: stefa
"""

from __future__ import print_function
from dateutil.parser import parse as dtparse
from datetime import datetime as dt
from datetime import timedelta, date

import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']



event_template = {
  
  
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}

def calendar_interface():
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except:
        print('An error occurred')

def add_block_to_calendar(cal_int, start, end, user_email, robot_id, description):
    start = start.isoformat()
    end = end.isoformat()
    print(start)
    print(end)
    event_params = {
        'description': description,
        'location': robot_id,
        'attendees': [
          {'email': user_email},
        ],
        'start': {
          'dateTime': start,
          'timeZone': 'America/New_York',
        },
        'end': {
          'dateTime': end,
          'timeZone': 'America/New_York',
        },

    }
    
    event = {**event_params, **event_template}
    
    result = cal_int.events().insert(calendarId='3glgk28tep6iqq7aj71rka1lpg@group.calendar.google.com', body=event).execute()
    return result

    
if __name__ == '__main__':
    cal_int = calendar_interface()
    start = dt.now()
    end = dt.now() + timedelta(hours=12)
    user_email = 'stefanmgolas@gmail.com'
    robot_id = '00001'
    description = 'test_event'
    a = add_block_to_calendar(cal_int, start, end, user_email, robot_id, description)
    print(a)


