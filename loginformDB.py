#_*_coding:utf-8_*_
import urllib2
import requests
import time
import random
import cookielib
import pymongo
from bs4 import BeautifulSoup
import json
import re
from weiboDB import bangdan24



class weiboYZM:
    def __init__(self):

        self.headers={
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            }
        self.cookie=cookielib.LWPCookieJar()
        self.cookiehandler=urllib2.HTTPCookieProcessor(self.cookie)
        self.client=pymongo.MongoClient('localhost',27017)
        self.COL=self.client['WeiboLogin']
        self.cookieDOC=self.COL['cookieDoc']



    def _Init(self):
        dict1=self.cookieDOC.find_one({},{'_id':0,'ownner':0,'pwd':0,'purpose':0})
        cookiestr=''
        for i in dict1:
            cookiestr+=(i+'='+dict1[i]+';')
        print cookiestr
        self.headers['cookie']=cookiestr
        print self.headers

    def run(self):
        self._Init()
        self.openner=urllib2.build_opener(self.cookiehandler)
        for jsonpagenumber in range(10):
            time.sleep(random.randint(2,5))
            url1='http://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803&pagebar=0&tab=home&current_page='+str(jsonpagenumber+1)+'&pre_page='+str(jsonpagenumber)+'&page='+str(jsonpagenumber)+'&pl_name=Pl_Core_NewMixFeed__3&id=102803&script_uri=/102803&feed_type=1&domain_op=102803'
            self.request=urllib2.Request(url=url1,headers=self.headers)
            response=self.openner.open(self.request)
            print response.url
            responsedata= response.read()
            # print responsedata
            #5-16日发现这里可能存在跳转,原因很有可能是因为cookie中的某些值过期了,要么更新cookie,要么这下边判断,然后再重新定位进入
            #重新定位不行,一定要更新cookies.也就是后边的那几个网页要依次访问了.
            #5-17微博的cookie一天就会过期
            try:
                datajson = json.loads(responsedata)#如果过期就会跳转到js,加载就会失败,就会跳转到后边的更新cookie和再次登录模块
            except Exception as e:
                print e,'\n'
                #依次访问登录时会访问的3个页面,不要错过任何一个cookie
                self.request.url='http://login.sina.com.cn/crossdomain2.php?action=login'
                self.openner.open(self.request)
                self.request.url='http://i.sso.sina.com.cn/js/ssologin.js'
                self.openner.open(self.request)
                time.sleep(3)#记得某个页面跳转需要等待时间,忘了是哪一个了,不过写在这里应该没事.一切都是为了逼真
                self.request.url='https://login.sina.com.cn/'
                self.openner.open(self.request)


                #dataEncode中的cookie更新代码
                cookiedict = {}
                for j in self.cookie:
                    cookiedict[j.name] = j.value
                cookiedict['ownner'] = '17082779265'  #用来判断这个cookies是谁的
                cookiedict['pwd'] = 'a123456'
                self.cookieDOC.update({'ownner': cookiedict['ownner']}, {'$set': cookiedict}, upsert=True)


                #更新headers后再访问24小时榜单的json,看看能返回什么信息
                self._Init()
                time.sleep(random.randint(2, 5))
                url1 = 'http://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803&pagebar=0&tab=home&current_page=' + str(
                    jsonpagenumber + 1) + '&pre_page=' + str(jsonpagenumber) + '&page=' + str(
                    jsonpagenumber) + '&pl_name=Pl_Core_NewMixFeed__3&id=102803&script_uri=/102803&feed_type=1&domain_op=102803'
                self.request = urllib2.Request(url=url1, headers=self.headers)
                response = self.openner.open(self.request)
                print response.url
                responsedata = response.read()









            datajson=json.loads(responsedata)
            datajsonsoup=BeautifulSoup(datajson['data'],'lxml')
            # for j in datajsonsoup:
            #     print j

            for i in datajsonsoup.select('div["tbinfo"]'): #div > div.WB_feed.WB_feed_v3.WB_feed_v4
                #后边代码不要出现i了,以免出现问题

                thisclass=bangdan24()
                print '\n'
                thisclass.mid = i.get('mid')
                detail= i.select('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_info > a')

                # 对用户是否是新浪微博会员,个人认证等的一些信息提取
                userstatus=[]
                for j in detail:
                    if j.get('title'):
                        temporary= j.get('title').encode('utf-8')
                        print temporary
                        userstatus.append(temporary)
                    else:
                        temporary= j.select('i')[0].get('title').encode('utf-8')
                        print '个人认证微博',temporary
                        userstatus.append(temporary)

                print userstatus,'----',len(userstatus)
                thisclass.username=userstatus[0]
                if '微博会员' in userstatus:
                    thisclass.is_vip=True
                if '微博个人认证'  in userstatus:
                    thisclass.persional_certificate=True
                if '超级网红节' in userstatus:
                    thisclass.super_wanghongjie=True
                # for state in userstatus:
                #     print state




                for j in i.select(' div.WB_feed_detail.clearfix > div.WB_detail > div.WB_from.S_txt2 > a'):
                    if j.get('name'):
                        # print '帖子链接-',j.get('href')
                        thisclass.forum_url=j.get('href')#获得对饮帖子的链接
                        # print '用户id--',j.get('name')#获取用户的id
                        thisclass.user_id=j.get('name')
                        # print '时间----',j.get('date')
                        thisclass.publish_time=j.get('date')
                    else:
                        # print '来自----',j.text
                        thisclass.come_from=j.text
                for j in  i.select(' div.WB_feed_detail.clearfix > div.WB_face.W_fl > div > a'):
                    # print '该用户的主页',j.get('href')
                    thisclass.user_homepage=j.get('href')
                for j in i.select(' div.WB_feed_detail.clearfix > div.WB_detail > div.WB_text.W_f14'):
                    # print j.text
                    thisclass.content=j.text

                thisclass.deal()


            # for i in datajsonsoup.select('div.WB_info'):
            #     print '用户昵称-------',i.text
            #     # print '用户链接-------',i.select('a')[0].get('href')
            #     print '用户昵称2------',i.select('a')[0].get('nick-name').strip()
            #
            #
            # for i in datajsonsoup.select('div.WB_from.S_txt2 > a'):
            #     print i.get('name')
            #     if i.get('name'):
            #         print '帖子的具体链接---',i.get('href')
            #         print 'publisher_id---',i.get('name')
            #         print '发帖时间--------',i.get('date')
            #     else:
            #         print '来自客户端-------',i.text
            #
            #
            # for i in datajsonsoup.select('div.WB_text.W_f14'):
            #     print '======不知道是什么',i.text




            # fileresponse=file('/media/administrator/3804CCCA04CC8C76/project/nouse/sina/responsedata_bangdan.txt','a+')
            with open('/media/administrator/3804CCCA04CC8C76/project/nouse/sina/responsedata_bangdan.txt','a+') as fl:
                fl.write(responsedata)
            fl.close()



if __name__ == '__main__':
    a=weiboYZM()
    a.run()
    #http://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803&pagebar=0&tab=home&current_page=1&pre_page=0&page=0&pl_name=Pl_Core_NewMixFeed__3&id=102803&script_uri=/102803&feed_type=1&domain_op=102803
    #数据源的格式
