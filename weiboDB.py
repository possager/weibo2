#_*_coding:utf-8_*_
import pymongo
class bangdan24:
    def __init__(self):
        self.mid=None
        self.username=None
        #用户个人微博状态
        self.persional_certificate=False
        self.super_wanghongjie=False#超级网红节,不知道后边还会不会有这个标签,将来调试可以删除2017年5月18日
        self.is_vip=False

        self.forum_url=None
        self.user_id=None
        self.publish_time=None
        self.come_from=None
        self.user_homepage=None
        self.content=None

        self.client=pymongo.MongoClient('localhost',27017)
        self.DB=self.client['Weibocontent']
        self.COL=self.DB['bangdan24']

        self.proxyIPport=None
        self.proxyIP=None
        self.purpose=None


    def _InitialDB(self):
        self.COL.create_index([('publish_time',pymongo.ASCENDING),('mid',pymongo.DESCENDING)],unique=True)

    def deal(self):
        self._InitialDB()
        dict1={
            'mid':self.mid,
            'username':self.username,
            'persional_certificate':self.persional_certificate,
            'is_vip':self.is_vip,
            'super_wanghongjie':self.super_wanghongjie,
            'forum_url':self.forum_url,
            'user_id':self.user_id,
            'publish_time':self.publish_time,
            'come_from':self.come_from,
            'user_homepage':self.user_homepage,
            'content':self.content,
            'proxyIP':self.proxyIP,
            'proxyIPport':self.proxyIPport,
            'purpose':self.purpose
        }
        try:
            self.COL.insert(dict1)
        except Exception as e:
            print e

    def DBshow(self):
        print '<热榜24小时数据库>数量---------->',self.COL.find().count()



class bangdan24comments:
    def __init__(self):
        self.ownnerweibomid=None
        self.userid=None
        self.username=None
        self.content=None
        self.publishtime=None
        self.other=None


