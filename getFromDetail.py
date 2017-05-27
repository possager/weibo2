import urllib2
from bs4 import BeautifulSoup
import json
import time
import cookielib
import cookielib
import pymongo


class FormDetail:
    def __init__(self,url=None):
        self.IPproxy=None
        self.IPproxyPort=None
        self.IPproxyType='Https'

        self.client=pymongo.MongoClient('localhost',27017)
        self.COL=self.client['Weibocontent']
        self.DOC=self.COL['bangdan24']


        self.url=url
        self.headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
        self.cookie=cookielib.LWPCookieJar()
        self.cookieHandler=urllib2.HTTPCookieProcessor(self.cookie)
        self.openner=urllib2.build_opener(self.cookieHandler)
        # self.request=urllib2.Request(url=self.url,headers=self.headers)
        self.request=None
        self.response=None

    def urlget(self):
        for i in self.DOC.find({},{'_id':0,'forum_url':1}).limit(10):
            yield i['forum_url']
            # self.DOC.update({'forum_url':i['forum_url']},{'dealed':True},upsert=True)

    def run(self):
        beforeurllist=[
            'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)',
            'http://login.sina.com.cn/crossdomain2.php?action=login',
            'http://i.sso.sina.com.cn/js/ssologin.js',
            'https://login.sina.com.cn/cgi/pin.php',
            'http://weibo.com/login.php',
            'https://passport.weibo.com/visitor/visitor',
            'http://weibo.com/aj/v6/top/topnavthird',
            'https://passport.weibo.com/visitor/visitor?a=incarnate&t=bGyvqLA0Up0oVHO2rqeXYGnrHwu%2FsC9yhjCdAQ6ooxY%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.10277698794252332',
            'https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMue28jf8NxqwJRmP8dyGngZIhxyw_EieKYJ574JRMxHRl-yT83qnFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W555Mkrw4C8Pv59U1xT0MxL&from=weibo&_rand=0.2432791179006497',
            'http://weibo.com',
            'https://login.sina.com.cn/',
        ]
        for i in beforeurllist:
            request=urllib2.Request(url=i,headers=self.headers)
            data=self.openner.open(request)
            print data.headers
            time.sleep(0.5)

        print self.cookie
        for i in self.urlget():
            redict_url=''
            while 'http://weibo.com/1258954655/F3EDzbEyh' not in redict_url:
                self.request=urllib2.Request(url=i,headers=self.headers)
                data=self.openner.open(self.request)
                print data.url
                redict_url=data.url
                datasoup=BeautifulSoup(data.read(),'lxml')
                print datasoup
                time.sleep(5)

        # response=self.openner.open(self.request)
        # data=response.read()
        # datasoup=BeautifulSoup(data,'lxml')


if __name__ == '__main__':
    thisclass=FormDetail()
    thisclass.run()