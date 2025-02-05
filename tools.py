from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials



class GoogleCalendarTool:
    def __init__(self, credentials):
        creds = Credentials.from_authorized_user_file(credentials, ['https://www.googleapis.com/auth/calendar'])
        self.service = build('calendar', 'v3', credentials=creds)

    def check_avaliability(self, booking_details):

        return "avaliable"
    
    def book_event(self, booking_details):
        event = self.service.events().insert(calendarId='primary', body=booking_details).execute()
        return event