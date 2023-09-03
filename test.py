from datetime import datetime

from api.bookings.ApiBookings import ApiBookings
from api.bookings.Booking import Booking
from api.members.ApiMembers import ApiMember
from api.meetings.ApiMeetings import ApiMeetings
from api.meetings.Meeting import Meeting
from api.settings import datetime_format_str_api

api_meetings = ApiMeetings("http://127.0.0.1:8000")
api_bookings = ApiBookings("http://127.0.0.1:8000")
meetings = api_meetings.get_meetings()

# for meeting in meetings:
#     d = meeting.get_free_tickets()

# m = api_meetings.get_meeting_by_pk(2)
# r = m.check_booking_by_td_id(123456789)

d = api_bookings.get_booking_by_pk(3)

n = Booking(date_time=datetime.now().strftime(datetime_format_str_api), is_paid=True)
api_bookings.add_booking(n, 5, 3)
