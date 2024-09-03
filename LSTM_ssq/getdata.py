import requests
import json
import pandas as pd

def getdata():
    url = 'http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice'
    params = {
        'name': 'ssq',
        'issueCount': '',
        'issueStart': '',
        'issueEnd': '',
        'dayStart': '',
        'dayEnd': '',
        'pageNo': '1',
        'pageSize': '9999',
        'week': '',
        'systemType': 'PC'
    }
    response = requests.get(url, params=params)
    jsondata = response.json()
    if jsondata['state']==0:
        data = []
        for item in jsondata['result']:
            print(item['blue'])
            blue_ball=item['blue']
            red_balls=item['red'].split(',')
            data.append([item['code'], int(red_balls[0]), int(red_balls[1]), int(red_balls[2]), int(red_balls[3]), int    (red_balls[4]), int    (red_balls[5]),int(blue_ball)])
        df = pd.DataFrame(data, columns=['期号', 'red1', 'red2', 'red3', 'red4', 'red5','red6', 'blue'])
        df.to_csv('data.csv', index=False)  
getdata()