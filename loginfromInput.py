#_*_coding:utf-8_*_
import urllib2
import cookielib
import time
import pymongo
import re
import json
import random
import binascii
import rsa
import base64

from bs4 import BeautifulSoup




class weibologin:
    def __init__(self,username,password,useProxy=False):
        self.username=username
        self.password=password
        self.useIPproxy=useProxy
        self.header = None
        self.cookie = None
        self.proxyhandler = None
        self.openner = None
        self.client = pymongo.MongoClient('localhost', 27017)
        self.COL = self.client['WeiboLogin']
        self.cookieDOC = self.COL['cookieDoc']

        self.proxyIP = None
        self.proxyIPport = None
        self.proxytype = None
        self.purpose = None

        self.proxyCOL = self.client['IpProxy2']
        self.proxyDOC = self.proxyCOL['weiboDOC']


    def initPara(self):#用来初始化一些基本的如header,将来可能还会有para等参数
        self.header={
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        return self

    def getPreLoginJS(self):#新浪微博登录前
        url='http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)'
        response=self.openner.open(url).read()
        data1=re.findall(r'\((\{.*?\})\)',response)[0]
        datajson=json.loads(data1)
        self.rsakv=datajson['rsakv']
        self.nonce=datajson['nonce']
        self.pubkey=datajson['pubkey']
        self.servertime=datajson['servertime']

        return self

    def enableCookie(self,purpose=None):#default来表示默认的用途,就是随便使用,若是想制定爬去某个层次的内容的话,在default里边支出

        self.purpose=purpose
        requestsproxy=None
        if self.useIPproxy:
            proxylist=[]
            for i in self.proxyDOC.find({'used':False},{'_id':0}).limit(30):
                proxylist.append({
                    'ip':i['ip'],
                    'port':i['port'],
                    'proxytype':i['proxytype']
                })

            proxyinthis=proxylist.pop()

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


        #需要在这里检查一下代理ip是否可用,如果可用再返回
            requestsproxy=urllib2.Request(url='http://login.sina.com.cn/crossdomain2.php?action=login',headers=self.header)
        data=self.openner.open(requestsproxy).read()
        if len(data)>100:
            pass
        else:#如果这个代理ip不能用,先从数据库中删除,之后再来一次
            self.proxyDOC.delete_one({'ip':self.proxyIP})
            self.enableCookie()

        return self


    def login(self):
        loginURL='https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_='+str(int(time.time()*1000))

        #-------------------5-12
        #这次在一开始就直接加入验证码输入框,因为一开始输入验证的话至少还有提示说验证码错误.而之后再处理验证码,则总是不对.
        #而这次添加在第一次访问时请求验证码就能登录成功,可能与我这个账号本来需要验证码登录有关,如果将来不需要验证码登录的话,就知道这种
        #   继续请求验证码的方法会不会导致错误.
        headersimg = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'referer': 'https://login.sina.com.cn/signup/signin.php?entry=sso'
        }
        imageresponseSuccessed=0
        while imageresponseSuccessed==0:
            #请求图片时区分图片的关键是是ulogin_img
            #所以这里用代理ip发送登录信息,自己的ip来获取验证码,注意只要cookie中的ulogin_img
            try:
                cookiehandlerYZZM=urllib2.HTTPCookieProcessor(self.cookie)
                self.openner=urllib2.build_opener(cookiehandlerYZZM)
                cookieheader=''
                requestYZM = urllib2.Request(
                    url='https://login.sina.com.cn/cgi/pin.php?' + str(random.randint(10000000, 99999999)))
                imageresponse = self.openner.open(requestYZM).read()


                ###############
                # Image1=Image.frombuffer('RGB',(100,40),data=imageresponse)
                # Image._show(Image1)
                ############


                print self.cookie
                print cookieheader
                for i in self.cookie:
                    cookieheader+=i.name+'='+i.value+';'
                print cookieheader





                # imageresponse = self.openner.open(
                #     urllib2.Request(url='https://login.sina.com.cn/cgi/pin.php?' + str(random.randint(10000000, 99999999)),
                #                     headers=headersimg)).read()
                if imageresponse:
                    imageresponseSuccessed=1
                    time.sleep(2)
            except Exception as e:
                print e
                time.sleep(3)
                imageresponseSuccessed=0

        timeimg=time.time()
        print int(timeimg*1000)
        with open('/media/administrator/3804CCCA04CC8C76/project/weiboAPI/YZM' + str(
                int(timeimg * 1000)) + '#' + '.png', 'w+') as imgfl:
            imgfl.write(imageresponse)
        imgfl.close()
        yanzhengma = raw_input('请输入验证码')
        print yanzhengma
        self.postdata['door'] = yanzhengma.encode('utf-8')

        #------登录成功!!!



        request1=urllib2.Request(headers=self.header,url=loginURL)
        responseInLogin=self.openner.open(request1).read()
        print responseInLogin
        time.sleep(10)


        responsedataLogin=responseInLogin.read()
        responseLoginJson=json.loads(responsedataLogin)
        print '-------',responsedataLogin
        print responseInLogin.url
        if responseLoginJson['retcode']=='0':
            print responseLoginJson['retcode']
            crossDomainUrlList=responseLoginJson['crossDomainUrlList']
            # print crossDomainUrlList

            self._webread(crossDomainUrlList[0])
            self._webread(crossDomainUrlList[1])
            self._webread(crossDomainUrlList[2])
            self._webread('http://login.sina.com.cn/crossdomain2.php?action=login')
            self._webread('http://i.sso.sina.com.cn/js/ssologin.js')
            self._webread('https://login.sina.com.cn/')

            # -----------------5-12
            cookiedict = {}  # 用来在下边生成字典,再存在mongodb中
            for i in self.cookie:
                cookiedict[i.name] = i.value

            cookiedict['ownner'] = self.username  # 以后根据这个字段来更新
            cookiedict['pwd'] = self.password
            cookiedict['proxyIPport']=self.proxyIPport
            cookiedict['proxyIP']=self.proxyIP
            cookiedict['purpose']=self.purpose

            self.cookieDOC.update({'ownner': cookiedict['ownner']}, {'$set': cookiedict}, upsert=True)
            self.proxyDOC.update({'ip':self.proxyIP},{'$set':{'used':True}},upsert=True)#因为一个ip一个账号,所以这个账号被使用了要被标记.

            # --------
        #验证码登录失败就会进入下边这段代码,            #这下边的代码效果不保证,一般正常情况下肯定失败.
        else:
            print responseLoginJson['retcode']
            print responseLoginJson['reason']#the reason why fialed to login

            headersimg={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                'referer': 'https://login.sina.com.cn/signup/signin.php?entry=sso'
            }
            imageresponse=self.openner.open(urllib2.Request(url='https://login.sina.com.cn/cgi/pin.php?'+str(random.randint(10000000,99999999)),headers=headersimg)).read()
            ULONG_IMG=None
            for i in self.cookie:
                print i.value
                ULONG_IMG=i.value
            timeimg=time.time()
            print timeimg
            with open('/media/administrator/3804CCCA04CC8C76/project/weiboAPI/YZM'+str(int(timeimg*1000))+'#'+ULONG_IMG+'.png','w+') as imgfl:
                imgfl.write(imageresponse)
            imgfl.close()

            yanzhengma=raw_input('请输入验证码')
            print yanzhengma
            self.postdata['door']=yanzhengma.encode('utf-8')
            self.header['Cookie']='ULOGIN_IMG='+ULONG_IMG
            self.header['referer']='https://login.sina.com.cn/signup/signin.php?entry=sso'
            self.header['Accept-Encoding']='gzip, deflate, br'
            self.header['Accept-Language']='zh-CN,zh;q=0.8'
            self.header['Connection']='keep-alive'
            self.header['Content-Length']=531
            self.header['Content-Type']='application/x-www-form-urlencoded'
            self.header['Host']='login.sina.com.cn'
            self.header['Accept']='*/*'

            self.login()


if __name__ == '__main__':
    thisclass=weibologin(username='17023470263',password='asdf112915')
    thisclass.initPara()
    thisclass.enableCookie()
    thisclass.getPreLoginJS()
    thisclass