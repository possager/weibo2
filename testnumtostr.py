import urllib2
import string
import random

string1='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789%'
str1=''
for i in range(len('VIPZmdsCw%2BQyrNnxcNovFvODkEmJ5oUDUTdByeL5Pco')):
    str1+=string1[random.randint(0,62)]
print str1