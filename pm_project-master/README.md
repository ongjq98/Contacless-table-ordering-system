# pm_project

Project description:
Each group is contracted by the CIO of UOW to develop a booking system to use the video conferencing
tool (e.g. Zoom or Webex) for UOW students. The tool shall allow for at least 5 video conference
channels. A channel is like a room with many sessions (bookings). As a minimum requirement, the
system should provide the following functions:
• Channel creation and management: only done by a staff user, staff can create and launch a new
channel (sessions can only be booked by students after a channel is launched), staff can adjust the
date and/or time and/or attendee capacity on an existing channel.
• Session booking: only done by a student user, student can view the list of channels, book one or
more sessions at any of the channels, can modify an existing booking, can cancel an existing
booking


booking system website created using : python flask, html bootstrap, postgresql


Summary: 

REQUIRED FUNCTIONS:

STAFF USERS:
- create channels
- adjust date & time
- decide on capacity of channels

STUDENT USERS:
- view available channels
- book one or more sessions
- modify or cancel existing booking


CHANNEL & SESSION definition:
- channel D&T input range - 1-7days (effective on the day channel is created)
- 7 session to choose 1. 0800-1000, 2. 1000-1200, 3.1200-1400, 4. 1400-1600, 5. 1600-1800, 6. 1800-2000, 7. 2000-2200


TASKS:
1. Create login page to differentiate staff and student
2. Decide on sql table and respective attributes
3. Create Page for staff to create channels
   - able to input how many days channel will last (1-7), capacity
   - after creation, able to view existing channels
4. Create page for student to view all channels
   - able to view all booked and unbooked channel sessions
   - for unbooked sessions, have options to book
5. Create 'my bookings' page for students so that they can modify and cancel their bookings
   - if booked sessions are cancelled, becomes available again on website.
