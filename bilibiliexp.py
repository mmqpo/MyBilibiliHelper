#!/usr/bin/env python
# coding=utf-8

import MySQLdb,requests,json
from apscheduler.schedulers.blocking import BlockingScheduler
import myapi
from accountclass import bilibili
import myproxy
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

list_abled =['15824397397','17367078621','15127529708','13306522935']

def connectdb():
    print('连接到mysql服务器...')
    db = MySQLdb.connect("localhost","root","123456","bilibili")
    print('数据库连接成功!')
    return db

def createtable(db):
    cursor = db.cursor()
    sql = """CREATE TABLE Account (
            ID CHAR(50) NOT null,
            Password CHAR(50) NOT null,
            Access_Key CHAR(50),
            Cookies TEXT,
            coinnum() INT,
            aid CHAR(50),
            a_type INT)，
            finished BOOLEAN,
            logined BOOLEAN,
            watched BOOLEAN,
            shared BOOLEAN,
            coin_added BOOLEAN,
            double_watch BOOLEAN,
            s2c BOOLEAN,
            signed BOOLEAN,
            current_level INT，
            last_like_dynamic INT"""

    cursor.execute(sql)

def insertdb(db,ID,Password,a_type):
    cursor = db.cursor()
    access_key=myapi.get_access_key(ID,Password)
    cookies=myapi.get_cookies(access_key)
    if(access_key == '-1'):
        print '密码错误'
        return
    if a_type != 4:
        sql = """INSERT INTO Account
         VALUES ("%s", "%s","%s","%s",0,"3770834",%d,False,False,False,False,False,False,False,False,0,0)""" %(ID,Password,access_key,cookies,a_type)
    else:
        sql = """INSERT INTO Account
         VALUES ("%s", "%s","%s","%s",0,"3770834",%d,False,False,False,False,True,True,True,False,0,0)""" %(ID,Password,access_key,cookies,a_type)

    try:
        cursor.execute(sql)
        print "%s 插入成功" %ID
        db.commit()
    except:
        print '插入数据失败!'
        print sql
        db.rollback()

def querydball(db):
    cursor = db.cursor()
    id_list = []

    sql = "SELECT * FROM Account WHERE finished = False"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            ID = row[0]
            id_list.append(ID)
    except:
        print "Error: unable to fecth data"
    return id_list

def deletedb(db,ID):
    cursor = db.cursor()

    sql = "DELETE FROM Account WHERE ID = '%s'" %ID

    try:
       cursor.execute(sql)
       db.commit()
    except:
        print '删除数据失败!'
        db.rollback()

def deleteallindb(db):
    cursor = db.cursor()

    sql = "DELETE FROM Account"

    try:
       cursor.execute(sql)
       db.commit()
    except:
        print '删除数据失败!'
        db.rollback()

def everyday_set(db):
    cursor = db.cursor()
    sql = "UPDATE Account SET finished = False,logined = False,watched = False,shared = False,coin_added = False,double_watch = False,s2c = False,signed = False"
    print sql
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print '更新数据失败!'
        db.rollback()
    sql = "UPDATE Account SET double_watch = True,s2c = True,coin_added = True WHERE a_type=4"
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print '更新数据失败!'
        db.rollback()

def flushdb(db,bilibili_temp):
    key_temp = myapi.get_access_key(bilibili_temp.ID,bilibili_temp.Password)
    cookies_temp = str(myapi.get_cookies(key_temp))
    cursor = db.cursor()
    sql = "UPDATE Account SET access_key = '%s' , cookies = \"%s\" WHERE ID = '%s'" % (key_temp,cookies_temp,bilibili_temp.ID)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print '更新数据失败!'
        db.rollback()
    return (key_temp,json.loads(cookies_temp.replace("'", '"')))

def querydb(db,id):
    cursor = db.cursor()
    sql = "SELECT * FROM Account WHERE ID = '%s'" %id
    cursor.execute(sql)
    result = cursor.fetchone()
    bilibili_temp=bilibili(result[0],result[1],result[2],result[3],result[5],result[6],result[7],result[8],result[9],result[10],result[11],result[12],result[13],result[14],result[16])
    if bilibili_temp.cookies_test() == False:
        print "%s cookies需重新获取" %id
        bilibili_temp.access_key,bilibili_temp.cookie = flushdb(db,bilibili_temp)
    if bilibili_temp.token_test() == False:
        print "%s token需重新获取" %id
        bilibili_temp.access_key,bilibili_temp.cookie = flushdb(db,bilibili_temp)
    return bilibili_temp

def back2db(db,bilibili_temp):
    cursor = db.cursor()
    sql = "UPDATE Account SET finished = %r,logined = %r,watched = %r,shared = %r,coin_added = %r,double_watch = %r,s2c = %r,signed = %r,current_level = %d,last_like_dynamic = %d WHERE ID='%s'" %(bilibili_temp.didfinished(),bilibili_temp.logined,bilibili_temp.watched,bilibili_temp.shared,bilibili_temp.coin_added,bilibili_temp.double_watch,bilibili_temp.s2c,bilibili_temp.signed,bilibili_temp.get_current_level(),bilibili_temp.last_like_dynamic,bilibili_temp.ID,)
    try:
        cursor.execute(str(sql))
        db.commit()
    except:
        print '更新数据失败!'
        db.rollback()


def closedb(db):
    db.close()

def task_begin(db):
    id_list = querydball(db)
    avlist = get_avlist()
    print avlist
    no_task_list=[]
    sign_num = 0
    login_num = 0
    watch_num = 0
    gift_num = 0
    #for id in id_list:
    for id in list_abled:
        print id
        bilibili_temp = querydb(db,str(id))
        print bilibili_temp.Password
        print bilibili_temp.coin_num()
        if bilibili_temp.double_watch == False: #非三无小号
            if bilibili_temp.taskinfo_get() == True:   #双端任务
                bilibili_temp.double_watch = True
                bilibili_temp.receive_double()

        if bilibili_temp.logined == False:
            bilibili_temp.access_key,bilibili_temp.cookie = flushdb(db,bilibili_temp)
            if bilibili_temp.get_login_info() == False:   #
                    bilibili_temp.access_key,bilibili_temp.cookie = flushdb(db,bilibili_temp)
            else:
                bilibili_temp.logined = True

        if bilibili_temp.signed == False:
            if bilibili_temp.get_signinfo() == False:   #直播签到
                bilibili_temp.sign()
            else:
                bilibili_temp.signed = True

        if bilibili_temp.watched == False:
            if bilibili_temp.get_watchinfo() == False:  #每日观看视频任务
                bilibili_temp.watch(avlist[0])
            else:
                bilibili_temp.watched = True

        if bilibili_temp.shared == False:
            if bilibili_temp.get_share_info() == False:  #每日观看视频任务
                bilibili_temp.share(avlist[0])
            else:
                bilibili_temp.shared = True

        if bilibili_temp.s2c == False:
            if bilibili_temp.get_giftinfo() == False:   #是否已做每日兑换
                bilibili_temp.silver2coins()
            else:
                bilibili_temp.s2c = True

        if bilibili_temp.coin_added == False:
            if bilibili_temp.a_type in [0,2]:
                for av_temp in avlist[bilibili_temp.get_coin_add_num()/10:]:
                    if bilibili_temp.coin_num() == 0:
                        break
                    bilibili_temp.coin_add(av_temp)
                if bilibili_temp.get_coin_add_num() == 50 or (bilibili_temp.s2c == True and bilibili_temp.coin_num() == 0):
                    bilibili_temp.coin_added = True

        back2db(db,bilibili_temp)
        print '------------------'
def dynamic_task(db):
    for id in list_abled:
        bilibili_dynamic = querydb(db,id)
        bilibili_dynamic.heart_web('10166229')
        bilibili_dynamic.heart_mobile('10166229')
        if(id in ['15824397397']):
            bilibili_dynamic.thumb_and_comment_new()
            back2db(db,bilibili_dynamic)

def heart_beat(db):
    for id in list_abled:
        bilibili_dynamic = querydb(db,id)
        bilibili_dynamic.heart_web('10166229')
        bilibili_dynamic.heart_mobile('10166229')

def get_avlist():
    guichu_page = requests.get('https://www.bilibili.com/ranking/all/119/1/1').text
    avlisttmp = re.findall('/av(.*?)/',guichu_page)
    avlist = {}.fromkeys(avlisttmp).keys()
    return avlist[:5]

def main():
    db = connectdb()    # 连接MySQL数据库
    #createtable(db) #建立表
    #insertdb(db,ID,Password,type)    #向数据库中插入账号
    scheduler = BlockingScheduler()
    scheduler.add_job(everyday_set, 'cron', hour=0, minute=2,args=[db])
    scheduler.add_job(heart_beat, 'cron', minute='*/5', args=[db])
    scheduler.add_job(task_begin, 'cron', hour=0, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=1, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=2, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=3, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=4, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=5, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=6, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=7, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=8, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=9, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=10, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=11, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=12, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=13, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=14, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=15, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=16, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=17, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=18, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=19, minute=3,args=[db])
    scheduler.add_job(task_begin, 'cron', hour=20, minute=3,args=[db])
    scheduler.start()
    closedb(db)

if __name__ == '__main__':
    main()
