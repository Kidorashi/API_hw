import requests
import json
import urllib.request
import re
import html
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    return json.loads(requests.get(api_request).text)

def dicting():
    group_info = vk_api('groups.getById', group_id='today_is_okay', v='5.63')
    group_id = group_info['response'][0]['id']

    item_count=200
    posts=[]
    while len(posts) < item_count:
        result = vk_api('wall.get', owner_id=-group_id, v='5.63', count=100, offset=len(posts))
        posts += result['response']["items"]
    return posts

def clear(string): #тотальная чистка
    string = html.escape(string)
    string = re.sub('<a class="pi_greeting".*?</a>', '', string)
    string = re.sub('&amp.*?[0-9]*?;', '', string)
    string = re.sub('&lt.*?&gt;', '', string)
    string = re.sub('#?[0-9]*?', '', string)
    string = string.replace('.', ' ')
    string = string.replace(',', ' ')
    string = string.replace(';', ' ')
    string = string.replace(':', ' ')
    string = string.replace('-', ' ')
    string = string.replace('?', ' ')
    string = string.replace('!', ' ')
    string = string.replace('^', ' ')
    string = string.replace('(', ' ')
    string = string.replace(')', ' ')
    string = string.replace('+', ' ')
    string = string.replace('\n', ' ')
    string = string.replace('\\', ' ')
    string = string.replace('/', ' ')
    string = string.replace('_', ' ')
    string = string.replace('"', ' ')
    string = string.replace('—', ' ')
    string = string.replace('~', ' ')
    string = string.replace('@', ' ')
    string = string.replace('&', ' ')
    string = string.replace('  ', ' ')
    string = string.replace('quot', '')
    return string

def leng(text): #считает длину текста
    n=0
    for word in text:
        n+=1
    return n

def post_dicting (posts): #словарь id : len_text относится к постам
    data_dict={}
    item_count = 200
    n=1
    while n<item_count:
        ps=posts[n]['text']
        ps=clear(ps)
        ps=leng(ps)
        id=posts[n]['id']
        data_dict[id]=ps
        n+=1
    return data_dict

def idcomment(result, num, id_comment): #словарь id:comment
    mas1=[]
    mas2=[]
    len_p = 0
    count_p = 0
    aver_len = 0
    res = re.findall('<div class="pi_head">\\n<a class="pi_author" href="/(.*?)">.*</a>', result)
    for part in res:
        mas1.append(part)
    resu = re.findall('<div class="pi_body">\\n<div class="pi_text">(.*?)</div>', result)
    for part in resu:
        count_p += 1
        part=clear(part)
        part=len(part)
        len_p += part
        mas2.append(part)

    if count_p!=0:
        aver_len = len_p // count_p

    n=len(mas2)-1
    while n>=0:
        id_comment[mas1[n]]=mas2[n]
        n-=1
    return id_comment, aver_len

def collect_id(result): #set с id комментаторов
    peop_mas = []
    res = re.findall('<a class="pi_author" href="/(.*?)">.*</a>', result)
    if res != None:
        for part in res:
            if len(part) != 82:
                peop_mas.append(part)
    peop_set = set(peop_mas)
    return peop_set

def collect_idcomment(post_dict): #словарь средняя длина поста:средная длина коммента
    comment_dict={}
    id_comment={}
    for num in post_dict:
        aver_len=0
        req = urllib.request.Request(
            'https://api.vk.com/method/wall.getComment?post_id=https://vk.com/wall-78301923?own=1&w=wall-78301923_' + str(
                num))
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        id_comment, aver_len=idcomment(result, num, id_comment)
        comment_dict[post_dict[num]]=aver_len
    return id_comment, comment_dict

def aver(leng):
    for part in leng:
        n = len(leng[part])
        s = sum(leng[part])
        aver_len = s // n
        leng[part] = aver_len
    return aver_len

def city_len(id_comment):
    city_len = {}
    for name in id_comment:
        user_info = vk_api('users.get', user_ids=name, fields='city', v='5.63', count=100)
        if 'response' in user_info:
            for user in user_info['response']:
                if 'city' in user:
                    city = user['city']['title']
                    if city in city_len:
                        city_len[city].append(id_comment[name])
                    else:
                        city_len[city] = [id_comment[name]]
    city_len=aver(city_len)
    return city_len

def wat_age(age_leng):
    age_len = {}
    for date in age_leng:
        if len(date) > 5:
            n = len(date) - 4
            age = 2016 - int(date[n:])
            age_len[age] = age_leng[date]
    return age_len

def age_len(id_comment):
    age_leng = {}
    for name in id_comment:
        user_info = vk_api('users.get', user_ids=name, fields='bdate', v='5.63', count=100)
        if 'response' in user_info:
            for user in user_info['response']:
                if 'bdate' in user:
                    age = user['bdate']
                    if age in age_leng:
                        age_leng[age].append(id_comment[name])
                    else:
                        age_leng[age] = [id_comment[name]]
    age_leng=wat_age(age_leng)
    age_leng=aver(age_leng)
    return age_leng

def draw1(dict, title, xlabel, ylabel):
    X = []
    Y = []
    for part in dict:
        X.append(part)
        Y.append(dict[part])
    plt.bar(X, Y)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()
    plt.close()

def draw2(dict, title, xlabel, ylabel):
    bar_keys = np.arange(len(dict))
    bar_values = [int(dict[key]) for key in dict]
    bar_sticks = [str(key) for key in dict]
    plt.bar(bar_keys, bar_values, align='center')
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xticks(bar_keys, bar_sticks, rotation=90)
    plt.show()
    plt.close()

def draw3(dict, title, xlabel, ylabel):
    X = []
    Y = []
    for part in dict.items():
        Y.append(part)
        X.append(dict[part])
    plt.bar(X, Y)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()
    plt.close()

post_dict=dicting()
post_dict=post_dicting(post_dict) #словарь id : len_text
id_comment, comment_dict=collect_idcomment(post_dict) #словарь id:comment с повторами
title="Соотношение длины поста к средней длине комментария"
ylabel="Длина поста"
xlabel="Средняя длина комментария"
draw1(comment_dict, title, xlabel, ylabel)
city_len=city_len(id_comment)
title="Соотношение города к средней длине комментария"
xlabel="Город"
ylabel="Средняя длина комментария"
draw2(city_len, title, xlabel, ylabel)

age_len=age_len(id_comment)
title="Соотношение возраста к средней длине комментария"
ylabel="Возраст"
xlabel="Средняя длина комментария"
draw3(age_len, title, xlabel, ylabel)
