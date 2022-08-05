from django.db import models
from django.contrib.auth import get_user_model



# A user has will:
# 1. Sign up with their name, email, and phone number. 
# 2. Set up morning text and evening text times (needs to account for different time zones).
# 3. Write down short-term goals and long term goals with the date created and the deadline. 
# 4. On the Daily Game Plan page users will record and manage their daily Most Important Task, and up to 3 critical tasks. 
# 5. At the end of the day the user gives a score based on completion. 
# - A score of 2 means 100% complete, 1 means 50-99% complete, 0 means 0-49% complete. 
# - The Most Important Task (MIT) is always weighted the heaviest and is multiplied based on how many Critical Tasks (CTs) there are. 
# - If there are no critical tasks, the MIT is multiplied by 5. A score of 0 is 0 for the day, 1 is 5 for the day, and 2 is 10 for the day. 
# - If there is 1 CT, the MIT score is multiplied by 4. 
# - If there are 2 CTs, the MIT score is multiplied by 3. 
# - If there are 3 CTs, the MIT score is multiplied by 2. 
# There is always a highest total possible score of 10. 
# 6. There is a section for Notes and Other Tasks where they can write down whatever they want without being scored. 
# 7. There is a counter that keeps track of the number of days in a row they write in an MIT. 
# 8. The Score Sheet will keep track of their past 7-day point averages and monthly averages. 

# How auto-messaging will work. 
# 1. Users will receive a text message in the morning at the time they request, usually with a motivational quote, their MIT and CTs for the day. 
# 2. At the end of the day at the time they request users will receive a text to reflect on their day and assign scores. They will be prompted to write in the next day's MIT and CTs. 

# Back-end Capabilities I'll Need
# 1. Scheduling and creating the text of messages that will be sent. 
# 2. I need to be able to change variables within text messages such as names, quotes, and bodies of their message. 
# - For example: Column B will have their first name, column C will have a specific quote, column d will have the remaining body of the message. 

# This should be a good start for now. This is a beta test, so I'm building a Minimum Viable Product to have people try and get feedback on. I will make tweaks as we go, so it's important that the site can be edited.

class Task(models.Model):
    TASK_TYPE_MOST_IMPORTANT = 'Most Important'
    TASK_TYPE_CRITICAL = 'Critical'
    TASK_TYPE_OTHER = 'Other'
    TASK_TYPES = (TASK_TYPE_MOST_IMPORTANT, TASK_TYPE_CRITICAL, TASK_TYPE_OTHER)
    TASK_DUERATION_DAILY = 'Daily'
    TASK_DUERATION_LONG_SHORT_TERM = 'Long-Short term'
    TASK_DUERATIONS = (TASK_DUERATION_DAILY, TASK_DUERATION_LONG_SHORT_TERM)
    is_completed = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=1)
    type = models.CharField(max_length=20, choices=((i, i) for i in TASK_TYPES), default=TASK_TYPE_MOST_IMPORTANT)
    duration = models.CharField(max_length=20, choices=((i, i) for i in TASK_DUERATIONS), default=TASK_DUERATION_LONG_SHORT_TERM)

    def __str__(self):
        return self.name
