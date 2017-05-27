#_*_coding:utf-8_*_
import urllib2
import json
import time
import cookielib
import cookielib
import pymongo
import random

from bs4 import BeautifulSoup

from multiprocessing import pool



'''
https://passport.weibo.com/visitor/visitor?a=incarnate&t=VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.2885638640543249


https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMudFjUf8NxqwJRmP8cz23naoh1wwvEieKYKKkPJRMxHRl-yT83qmIbtRChV7nwFmXye52yVUZkAhThwiye2g..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFWqJ6czq2hVPEAeyoOC3XI&from=weibo&_rand=0.8391488535063187

'https://passport.weibo.com/visitor/visitor?a=incarnate&t=bGyvqLA0Up0oVHO2rqeXYGnrHwu%2FsC9yhjCdAQ6ooxY%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.10277698794252332',#这里边的有些东西是可以换的095不可以换,但是之前的貌似可以


'https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMue28jf8NxqwJRmP8dyGngZIhxyw_EieKYJ574JRMxHRl-yT83qnFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W555Mkrw4C8Pv59U1xT0MxL&from=weibo&_rand=0.2432791179006497',





VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco
VIPZmdsCw+QyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco既然每次js都是一样的,这里是隐身模式下请求的,所以这里肯定不会包含任何设备信息,ip信息等.
bGyvqLA0Up0oVHO2rqeXYGnrHwu%2FsC9yhjCdAQ6ooxY
因为submerge显示每一次请求js就是一样的,说明这里边的cookie生成肯定是根据前边的某个值来生成的.


_2AkMudFjUf8NxqwJRmP8  cz23naoh1wwv Eie KYKKkP JRMxHRl-yT83q mIbtRChV7nwFmXye52yVUZkAhThwiye2g..
_2AkMue28jf8NxqwJRmP8  dyGngZIhxyw_ Eie KYJ574 JRMxHRl-yT83q nFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..

0033WrSXqPxfM72-Ws9jqgMF55529P9D9 WFWqJ6czq2hVPEAeyoOC3XI
0033WrSXqPxfM72-Ws9jqgMF55529P9D9 W555Mkrw4C8Pv59U1xT0MxL
注意第一个这种类型的链接,后边的返回值可以从第一个链接的内容中获得,所以第一个链接会显得格外重要.
这是里边链接的格式,可以看出格式变化,自己构造即可,反正现在就这么试着
'''





class CookieGetWithoutLogin:
    def __init__(self,url=None,useProxy=False):
        self.IPproxy=None
        self.useIPproxy=useProxy

        self.client=pymongo.MongoClient('localhost',27017)
        self.COL=self.client['WeiboLogin']
        self.cookiewithoutDOC=self.COL['CookieWithoutLogin']
        # self.COL = self.client['WeiboLogin']
        self.cookieDOC = self.COL['cookieDoc']
        self.proxyCOL = self.client['IpProxy2']
        self.proxyDOC = self.proxyCOL['weiboDOC']


        self.proxyIPport=None
        self.proxytype='Https'
        self.proxyIP = None
        self.purpose = None
        self.proxyhandler = None

        self.url=url
        self.header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
        self.cookie=cookielib.LWPCookieJar()
        self.cookieHandler=None
        self.openner=None


        self.request=None
        self.response=None

    def enableCookie(self,purpose=None):#default来表示默认的用途,就是随便使用,若是想制定爬去某个层次的内容的话,在default里边支出

        self.purpose=purpose
        requestsproxy=None
        if self.useIPproxy:
            proxylist=[]
            for i in self.proxyDOC.find_one({'used':False},{'_id':0}):
                proxylist.append({
                    'ip':i['ip'],
                    'port':i['port'],
                    'proxytype':i['proxytype']
                })

            proxyinthis=proxylist.pop()
            self.proxyDOC.update({'ip':proxyinthis['ip']},{'$set':{'used':True}})

            self.proxyIP=proxyinthis['ip']#之所以把它写到self里,因为外边调用后如果成功了,会将self中的内容写到数据库中.
            self.proxyIPport=proxyinthis['port']
            self.proxytype=proxyinthis['proxytype']

            # self.proxyIP='122.70.141.42'
            # self.proxyIPport='80'
            # self.proxytype='https'

            print '-----------'+self.proxyIP+':'+self.proxyIPport


            self.cookie=cookielib.LWPCookieJar()
            self.cookieHandler=urllib2.HTTPCookieProcessor(self.cookie)

            self.proxyhandler = urllib2.ProxyHandler({proxyinthis['proxytype']: proxyinthis['proxytype']+'://%s:%s' % (self.proxyIP, self.proxyIPport)})
            self.openner = urllib2.build_opener(self.cookieHandler, self.proxyhandler)
            # proxy_support=urllib2.ProxyHandler({'http':'http://115.85.233.94:80'})
            # self.openner=urllib2.build_opener(self.cookieHandler,urllib2.HTTPHandler,proxy_support)
        else:
            self.cookieHandler=urllib2.HTTPCookieProcessor(self.cookie)
            self.openner=urllib2.build_opener(self.cookieHandler)#5-19去掉了,urllib2.HttpHandler
        # urllib2.install_opener(openner)
        # urllib2.install_opener(openner)


        #需要在这里检查一下代理ip是否可用,如果可用再返回,不管用没用代理,这里都可以,如果没用太低的话,delete就会删除不了东西.

        try:
            self.run()
        except Exception as e:
            print e
            self.proxyDOC.update({'ip': self.proxyIP},{'$set':{'drop':'can not use'}},upsert=True)
            self.enableCookie()

        # requestsproxy=urllib2.Request(url='http://login.sina.com.cn/crossdomain2.php?action=login',headers=self.header)
        # data=self.openner.open(requestsproxy).read()
        # if len(data)>100:
        #     pass
        # else:#如果这个代理ip不能用,先从数据库中删除,之后再来一次
        #     self.proxyDOC.delete_one({'ip':self.proxyIP})
        #     self.enableCookie()

        return self



    def urlget(self):
        for i in self.DOC.find({},{'_id':0,'forum_url':1}).limit(10):
            yield i['forum_url']
            # self.DOC.update({'forum_url':i['forum_url']},{'dealed':True},upsert=True)

    def run(self):


        url_visiter_visiter1='https://passport.weibo.com/visitor/visitor?a=incarnate&t='
        beforeurllist=[
            'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)',
            'http://login.sina.com.cn/crossdomain2.php?action=login',
            'http://i.sso.sina.com.cn/js/ssologin.js',
            # 'https://login.sina.com.cn/cgi/pin.php',
            'http://weibo.com/login.php',
            'https://passport.weibo.com/visitor/visitor',
            'http://weibo.com/aj/v6/top/topnavthird',
            'https://passport.weibo.com/visitor/visitor?a=incarnate&t=VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.10277698794252332',#这里边的有些东西是可以换的095不可以换,但是之前的貌似可以
            'https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMue28jf8NxqwJRmP8dyGngZIhxyw_EieKYJ574JRMxHRl-yT83qnFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W555Mkrw4C8Pv59U1xT0MxL&from=weibo&_rand=0.2432791179006497',
            'http://weibo.com',
            'https://login.sina.com.cn/',
        ]
        for i in beforeurllist:
            request=urllib2.Request(url=i,headers=self.header)
            data=self.openner.open(request,timeout=5000)
            print data.url
            print data.headers
            time.sleep(0.1)

        print self.cookie
        cookiedictwithoutlogin={}
        try:
            for i in self.cookie:
                cookiedictwithoutlogin[i['name']]=i['value']
                # self.cookiewithoutDOC.insert({i['name']:i['value']})
            # self.cookiewithoutDOC.insert({'tid':'VIPZmdsCw+QyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco=__095'})
            # self.cookiewithoutDOC.insert({'proxyIP':self.proxyIP})
            # self.cookiewithoutDOC.insert({'proxyIPport':self.proxyIPport})
            # self.cookiewithoutDOC.insert({'proxytype':self.proxytype})
            cookiedictwithoutlogin['tid']='VIPZmdsCw+QyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco=__095'
            cookiedictwithoutlogin['proxyIP']=self.proxyIP
            cookiedictwithoutlogin['proxyIPport']=self.proxyIPport
            cookiedictwithoutlogin['proxytype']=self.proxytype
            self.cookiewithoutDOC.insert(cookiedictwithoutlogin)
        except Exception as e:
            print e#153.101.205.25:3128--------203.110.170.50:80



        # for i in self.urlget():
        #     redict_url=''
        #     while 'http://weibo.com/1258954655/F3EDzbEyh' not in redict_url:
        #         self.request=urllib2.Request(url=i,headers=self.header)
        #         data=self.openner.open(self.request)
        #         print data.url
        #         redict_url=data.url
        #         datasoup=BeautifulSoup(data.read(),'lxml')
        #         print datasoup
        #         time.sleep(5)

        # response=self.openner.open(self.request)
        # data=response.read()
        # datasoup=BeautifulSoup(data,'lxml')


def runfunction(num):
    print num
    thisclass = CookieGetWithoutLogin(useProxy=True)
    thisclass.enableCookie()

if __name__ == '__main__':
    # thisclass=CookieGetWithoutLogin(useProxy=True)
    # thisclass.enableCookie()
    pool1=pool.Pool(processes=5)
    pool1.map(runfunction,[x for x in range(30)])
    pool1.join()
    pool1.close()
