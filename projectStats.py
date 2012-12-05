#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Citizen Cyberscience Centre
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from optparse import OptionParser
import pbclient
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

if __name__ == "__main__":
    # Arguments for the application
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    
    parser.add_option("-s", "--server", dest="api_url", help="PyBossa URL http://domain.com/", metavar="URL")
    parser.add_option("-k", "--api-key", dest="api_key", help="PyBossa User API-KEY to interact with PyBossa", metavar="API-KEY")
    parser.add_option("-a", "--app", dest="app", help="PyBossa app", metavar="APP")
    parser.add_option("-p", "--private", action="store_true", dest="private", default=False, help="Anonymize the data", metavar="PRIVATE")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    # Create App
    (options, args) = parser.parse_args()

    if not options.api_url:
        options.api_url = 'http://localhost:5000'
    pbclient.set('endpoint', options.api_url)

    if not options.api_key:
        parser.error("You must supply an API-KEY to create an applicationa and tasks in PyBossa")
        pbclient.set('api_key', options.api_key)

    if not options.app:
        options.app = 'besttile'

    if (options.verbose):
       print('Running against PyBosssa instance at: %s' % options.api_url)
       print('Using API-KEY: %s' % options.api_key)

    # Get all the task runs
    offset = 0
    app = pbclient.find_app(short_name=options.app)
    if (len(app) > 0):
        app = app[0]
        users = []
        anon_users = []
        auth_users =[]
        task_runs = pbclient.get_taskruns(app.id)
        dates = {} 
        dates_anon = {} 
        dates_auth = {} 
        hours = {}
        hours_anon = {}
        hours_auth = {}
        max_hours = 0
        max_hours_anon = 0
        max_hours_auth = 0

        # initialize hours keys
        for i in range(0,24):
            hours[u'%s' % i]=0
            hours_anon[u'%s' % i]=0
            hours_auth[u'%s' % i]=0
 
        import string
        while len(task_runs) > 0:
            for tr in task_runs:
                if tr.app_id == app.id:
                    # Check user stats
                    if (tr.user_id is None):
                        users.append(-1)
                        anon_users.append(tr.user_ip)
                    else:
                        users.append(tr.user_id)
                        auth_users.append(tr.user_id)

                    # Data for dates
                    date, hour = string.split(tr.finish_time, "T")
                    hour = string.split(hour,":")[0]

                    # Dates
                    if date in dates.keys():
                        dates[date] +=1
                    else:
                        dates[date] = 1

                    if tr.user_id is None:
                        if date in dates_anon.keys():
                            dates_anon[date] += 1
                        else:
                            dates_anon[date] = 1
                    else:
                        if date in dates_auth.keys():
                            dates_auth[date] += 1
                        else:
                            dates_auth[date] = 1

                    # Hours
                    if hour in hours.keys():
                        hours[hour] += 1
                        if (hours[hour] > max_hours):
                            max_hours = hours[hour]

                    if tr.user_id is None:
                        if hour in hours_anon.keys():
                            hours_anon[hour] += 1
                            if (hours_anon[hour] > max_hours_anon):
                                max_hours_anon = hours_anon[hour]

                    else:
                        if hour in hours_auth.keys():
                            hours_auth[hour] += 1
                            if (hours_auth[hour] > max_hours_auth):
                                max_hours_auth = hours_auth[hour]


            offset = offset + 100
            task_runs = pbclient.get_taskruns(app.id, offset=offset)


        userStats = dict(key="User Statistics", values=[])
        userAnonStats = dict(key="Anonymous Users", values=[], top5=[], locs=[])
        userAuthStats = dict(key="Authenticated Users", values=[], top5=[])
        dayNewStats    = dict(key="Anon + Auth",   values=[])
        dayTotalStats  = dict(key="Total", disabled="True", values=[])
        dayNewAnonStats  = dict(key="Anonymous", values=[])
        dayNewAuthStats  = dict(key="Authenticated", values=[])

        hourNewStats    = dict(label="Anon + Auth", disabled="True", values=[], max=0)
        hourNewAnonStats  = dict(label="Anonymous", values=[], max=0)
        hourNewAuthStats  = dict(label="Authenticated", values=[], max=0)

        total = 0
        import time
        # Dates
        for d in sorted(dates.keys()):
            # JavaScript expects miliseconds since EPOCH
            # New answers per day
            dayNewStats['values'].append(
                    [int(
                        time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                        ), 
                    dates[d]])

            # Total answers per day
            total = total + dates[d]
            dayTotalStats['values'].append(
                    [int(
                        time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                        ), 
                    total])

            # Anonymous answers per day
            if d in (dates_anon.keys()):
                dayNewAnonStats['values'].append(
                        [int(
                            time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                            ), 
                        dates_anon[d]])
            else:
                dayNewAnonStats['values'].append(
                        [int(
                            time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                            ), 
                        0])

            # Authenticated answers per day
            if d in (dates_auth.keys()):
                dayNewAuthStats['values'].append(
                        [int(
                            time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                            ), 
                        dates_auth[d]])
            else:
                dayNewAuthStats['values'].append(
                        [int(
                            time.mktime(time.strptime( d, "%Y-%m-%d"))*1000
                            ), 
                        0])

        # Hours 
        hourNewStats['max'] = max_hours
        hourNewAnonStats['max'] = max_hours_anon
        hourNewAuthStats['max'] = max_hours_auth
        for h in sorted(hours.keys()):
            # New answers per hour
            #hourNewStats['values'].append(dict(x=int(h), y=hours[h], size=hours[h]*10))
            if (hours[h] != 0):
                hourNewStats['values'].append([int(h), hours[h], (hours[h]*5)/max_hours])
            else:
                hourNewStats['values'].append([int(h), hours[h], 0])

            # New Anonymous answers per hour
            if h in hours_anon.keys():
                #hourNewAnonStats['values'].append(dict(x=int(h), y=hours[h], size=hours_anon[h]*10))
                if (hours_anon[h] != 0):
                    hourNewAnonStats['values'].append([int(h), hours_anon[h], (hours_anon[h]*5)/max_hours])
                else:
                    hourNewAnonStats['values'].append([int(h), hours_anon[h],0 ])

            # New Authenticated answers per hour
            if h in hours_auth.keys():
                #hourNewAuthStats['values'].append(dict(x=int(h), y=hours[h], size=hours_auth[h]*10))
                if (hours_auth[h] != 0):
                    hourNewAuthStats['values'].append([int(h), hours_auth[h], (hours_auth[h]*5)/max_hours])
                else:
                    hourNewAuthStats['values'].append([int(h), hours_auth[h], 0])

        # Count total number of answers for users
        anonymous = 0
        authenticated = 0
        for e in users:
            if e == -1:
                anonymous += 1
            else:
                authenticated += 1

        userStats['values'].append(dict(label="Anonymous", value=anonymous))
        userStats['values'].append(dict(label="Authenticated", value=authenticated))
        from collections import Counter
        c_anon_users = Counter(anon_users)
        c_auth_users = Counter(auth_users)

        for u in list(c_anon_users):
            userAnonStats['values']\
                    .append(dict(label=u, value=c_anon_users[u]))

        for u in list(c_auth_users):
            userAuthStats['values']\
                    .append(dict(label=u, value=c_auth_users[u]))

        # Get location for Anonymous users
        import pygeoip
        gi = pygeoip.GeoIP('dat/GeoIP.dat')
        gic = pygeoip.GeoIP('dat/GeoLiteCity.dat')
        top5_anon = []
        loc_anon = []
        for u in c_anon_users.most_common(5):
            loc = gic.record_by_addr(u[0])
            top5_anon.append(dict(ip=u[0],loc=loc, tasks=u[1]))

        for u in c_anon_users.items():
            loc = gic.record_by_addr(u[0])
            loc_anon.append(dict(ip=u[0],loc=loc, tasks=u[1]))

        userAnonStats['top5'] = top5_anon
        userAnonStats['locs'] = loc_anon

        # Exporting the data
        # Create a folder for the output
        import os.path 
        import shutil
        if not os.path.isdir(options.app):
            os.makedirs(os.path.join(options.app,'img'))
            shutil.copy("templates/img/navy_blue.png", 
                    os.path.join(options.app,'img'))
        anon_pct_taskruns = int((anonymous*100)/(anonymous+authenticated))
        # Check if we need to anonymize the data
        table_ip_random = {}
        table_user_id_random = {}
        if options.private:
            import random
            for u in userAnonStats['locs']:
                random_ip = "%s.%s.%s.%s" % (
                        random.randint(256,510),
                        random.randint(256,510),
                        random.randint(256,510),
                        random.randint(256,510))
                table_ip_random[u['ip']]=random_ip
                u['ip'] = random_ip
                # Modify a bit the Lat and Long too
                u['loc']['latitude'] += random.uniform(-0.5,0.5)
                u['loc']['longitude'] += random.uniform(-0.5,0.5)

            for u in top5_anon:
                if u['ip'] in table_ip_random.keys():
                    u['ip'] = table_ip_random[u['ip']]


            for v in userAnonStats['values']:
                if v['label'] in table_ip_random.keys():
                    v['label'] = table_ip_random[v['label']]

            low = len(auth_users)*-1
            top = len(auth_users)
            for i in range(0,len( auth_users )):
                random_id = random.randint(low,top)
                if auth_users[i] in table_user_id_random.keys():
                    auth_users[i] = table_user_id_random[auth_users[i]]
                else:
                    table_user_id_random[auth_users[i]]=random_id
                    auth_users[i] = random_id


            for v in userAuthStats['values']:
                v['label'] = table_user_id_random[v['label']]

            # Re-create the Counter
            c_auth_users = Counter(auth_users)



        import codecs
        f = open(os.path.join(options.app,'index.html'),'w')
        f.write(template.render(app=app, private=options.private, userStats=dict(
            anonymous=dict(
                users=len(userAnonStats['values']),
                taskruns=anonymous,
                pct_taskruns=anon_pct_taskruns,
                top5=top5_anon
                ),
            authenticated=dict(
                users=len(userAuthStats['values']),
                taskruns=authenticated,
                pct_taskruns=100-anon_pct_taskruns,
                top5=c_auth_users.most_common(5)
                )
            )).encode('utf-8', 'ignore'))
        f.close()
        f = open(os.path.join(options.app,'Stats.json'), 'w')
        import json
        Stats = dict(userStats=userStats, 
                userAnonStats=userAnonStats,
                userAuthStats=userAuthStats,
                dayStats=[
                    dayNewStats,
                    dayNewAnonStats,
                    dayNewAuthStats,
                    dayTotalStats],
                hourStats=[
                    hourNewStats,
                    hourNewAnonStats,
                    hourNewAuthStats,
                    ])
        tmp = "appStats = " 
        f.write("appStats = " + json.dumps(Stats) + ";")
        f.close()
    else:
        print "Ooops! Application not found!"