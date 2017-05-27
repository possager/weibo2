#_*_coding:utf-8_*_
import urllib2
from bs4 import BeautifulSoup
import json
import time
import cookielib
import cookielib
import pymongo
import random



'''
https://passport.weibo.com/visitor/visitor?a=incarnate&t=VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.2885638640543249


https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMudFjUf8NxqwJRmP8cz23naoh1wwvEieKYKKkPJRMxHRl-yT83qmIbtRChV7nwFmXye52yVUZkAhThwiye2g..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFWqJ6czq2hVPEAeyoOC3XI&from=weibo&_rand=0.8391488535063187

'https://passport.weibo.com/visitor/visitor?a=incarnate&t=bGyvqLA0Up0oVHO2rqeXYGnrHwu%2FsC9yhjCdAQ6ooxY%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.10277698794252332',#这里边的有些东西是可以换的095不可以换,但是之前的貌似可以


'https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s=_2AkMue28jf8NxqwJRmP8dyGngZIhxyw_EieKYJ574JRMxHRl-yT83qnFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..&sp=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W555Mkrw4C8Pv59U1xT0MxL&from=weibo&_rand=0.2432791179006497',





VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco
VIPZmdsCw+  QyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco既然每次js都是一样的,这里是隐身模式下请求的,所以这里肯定不会包含任何设备信息,ip信息等.
bGyvqLA0Up0oVHO2rqeXYGnrHwu%2FsC9yhjCdAQ6ooxY
因为submerge显示每一次请求js就是一样的,说明这里边的cookie生成肯定是根据前边的某个值来生成的.


_2AkMudFjUf8NxqwJRmP8  cz23naoh1wwv Eie KYKKkP JRMxHRl-yT83q mIbtRChV7nwFmXye52yVUZkAhThwiye2g..
_2AkMue28jf8NxqwJRmP8  dyGngZIhxyw_ Eie KYJ574 JRMxHRl-yT83q nFftRAkUXaBBP2h00j10Z7Ne2xSYkQMEg..

0033WrSXqPxfM72-Ws9jqgMF55529P9D9 WFWqJ6czq2hVPEAeyoOC3XI
0033WrSXqPxfM72-Ws9jqgMF55529P9D9 W555Mkrw4C8Pv59U1xT0MxL
注意第一个这种类型的链接,后边的返回值可以从第一个链接的内容中获得,所以第一个链接会显得格外重要.
这是里边链接的格式,可以看出格式变化,自己构造即可,反正现在就这么试着
'''





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


        url_visiter_visiter1='https://passport.weibo.com/visitor/visitor?a=incarnate&t='
        beforeurllist=[
            'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)',
            'http://login.sina.com.cn/crossdomain2.php?action=login',
            'http://i.sso.sina.com.cn/js/ssologin.js',
            'https://login.sina.com.cn/cgi/pin.php',
            'http://weibo.com/login.php',
            'https://passport.weibo.com/visitor/visitor',
            'http://weibo.com/aj/v6/top/topnavthird',
            'https://passport.weibo.com/visitor/visitor?a=incarnate&t=VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.10277698794252332',#这里边的有些东西是可以换的095不可以换,但是之前的貌似可以
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