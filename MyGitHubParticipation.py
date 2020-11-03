#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[184]:


import requests
import pandas as pd
import dateutil
import datetime
import pytz
from collections import Counter
import itertools
import sys
import warnings
warnings.filterwarnings("ignore")


#The following list should contain the due dates of all weeks as tuples. (10,9) means Oct 9. 
dates = [(10,9),
         (10,8),
         (10,15),
         (10,22),
         (10,29)]

# The following list should contain the issue ids of all the weeks. 
issue_ids = [1,2,3,5,6]
issues = "uchicago-computation-workshop/Fall2020/issues/"
current_github_accept = "application/vnd.github.squirrel-girl-preview+json"
#Put your GitHub access token here below inside the quotation marks. 
token = ''


def get_react(ID, react_deadline, auth = [], token = token):
    url_r = "https://api.github.com/repos/" + issues + "comments/"
    url_1 = url_r + str(ID) + "/reactions?page=1&per_page=100"
    url_2 = url_r + str(ID) + "/reactions?page=2&per_page=100"
    urls = [url_1, url_2]
    valid_users = []
    for url in urls:
        if token == '':
            single = requests.get(url, headers = {'Accept': current_github_accept}, auth = auth)
            r_users = single.json()
        else:
            headers = {'Accept': current_github_accept,'Authorization': 'token ' + token}
            single = requests.get(url, headers=headers)
            r_users = single.json()
        if len(r_users) > 0:
            r_df = pd.DataFrame(r_users)
            r_df['created_at_datetime'] = r_df['created_at'].apply(lambda x: dateutil.parser.parse(x))
            valid_r_df = r_df[r_df['created_at_datetime'] < react_deadline]
            valid_users += [user['login'] for user in valid_r_df.user]
        else:
            valid_users += []
    return(valid_users)


def get_weekly_count(week, auth = [], token = token):
    issue_id = str(issue_ids[week-1])
    url_c_1 = "https://api.github.com/repos/" + issues + issue_id + "/comments?page=1&per_page=100"
    url_c_2 = "https://api.github.com/repos/" + issues + issue_id + "/comments?page=2&per_page=100"
    urls = [url_c_1, url_c_2]
    comments = []
    for url_c in urls:
        if token == '':
            headers = {'Accept': 'application/vnd.github.v3+json'}
            r = requests.get(url_c, headers = headers, auth=auth)
        else:
            headers = {'Accept': 'application/vnd.github.v3+json','Authorization': 'token ' + token}
            r = requests.get(url_c, headers = headers)
        if r.status_code== 404:
            pass
        else:
            comments += r.json()
    if len(comments) == 0:
        github_df = None
        empty = True
    else: 
        comments_df = pd.DataFrame(comments)
        comments_df['created_at_datetime'] = comments_df['created_at'].apply(lambda x: dateutil.parser.parse(x))
        m, d = dates[week-1]
        date = datetime.datetime(2020,10,1)
        timezone = pytz.timezone("America/Chicago")
        d_aware = timezone.localize(date)
        comment_deadline = datetime.datetime(2020,m,d,0, tzinfo = d_aware.tzinfo)
        react_deadline = datetime.datetime(2020,m,d,11,20, tzinfo = d_aware.tzinfo)
        validcomments_df = comments_df[comments_df['created_at_datetime'] < comment_deadline]
        validcomments_df['reactions'] = validcomments_df['id'].apply(lambda x: get_react(x, react_deadline = react_deadline, auth = auth))
        validcomments_users = [user['login'] for user in validcomments_df['user']]
        comments_count = Counter(validcomments_users)
        valid_reactions = validcomments_df['reactions'].tolist()
        merged = list(itertools.chain(*valid_reactions))
        reactions_count = Counter(merged)
        columns = ['comments_%1d' %week, 'reacts_%1d' %week]
        github_df = pd.DataFrame([], columns = columns, index = validcomments_users)
        github_df.iloc[:,0] = pd.Series(comments_count)
        github_df.iloc[:,1] = pd.Series(reactions_count)
        empty = False
    return(github_df, empty)


# In[ ]:


if __name__=="__main__":  
    args = sys.argv
    if len(args)== 3:
        username, password = args[1:]
        auth = (username, password)
        github_df = get_weekly_count(1, auth = auth)[0]
        for i in range(2, (len(dates) + 1)):
            weekdf, empty = get_weekly_count(i, auth = auth)
            if empty:
                pass
            else:
                github_df = github_df.join(weekdf, how = 'outer')
        myrow = github_df.fillna(0).loc[[username]].iloc[0].tolist()
        for i in range(len(dates)):
            try:
                print('You made %1d comment(s) and %1d reactions to talk %1d.' % (myrow[i*2], myrow[i*2+1], i+1))
            except IndexError:
                pass
    elif len(args) == 2:
        username = args[1]
        if token == '':
            print("No token is provided.")
        else:
            github_df = get_weekly_count(1)[0]
            for i in range(2, (len(dates) + 1)):
                weekdf, empty = get_weekly_count(i)
                if empty:
                    pass
                else:
                    github_df = github_df.join(weekdf, how = 'outer')
            myrow = github_df.fillna(0).loc[[username]].iloc[0].tolist()
            for i in range(len(dates)):
                try:
                    print('You made %1d comment(s) and %1d reactions to talk %1d.' % (myrow[i*2], myrow[i*2+1], i+1))
                except IndexError:
                    pass
    else:
        print("wrong number of args")




