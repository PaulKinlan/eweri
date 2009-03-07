#!/usr/bin/env python

import wsgiref.handlers
import re # Regular expressions

import os
import datetime
import time
import urllib
import Base62to10

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

#
class Url(db.Model):
    "defines a url on the system"
    url = db.StringProperty()
    creationDate = db.DateTimeProperty()
    count = db.IntegerProperty()

class TopUrls:
    "Gets a list of the top urls on the system and returns them."
    def list(self):
        urlQuery = Url.all()
        urlQuery.order("-count")
        return urlQuery.fetch(limit = 5)
    
    def page(self, page):
        urlQuery = Url.all()
        urlQuery.order("-count")
        return urlQuery.fetch(10, (page - 1) * 10)
    
    def output(self, list = []):
        return

class NewUrls:
    "Gets a list of all the newest Urls"
    def list(self):
        urlQuery = Url.all()
        urlQuery.order("-creationDate")
        return urlQuery.fetch(limit = 5)
    
    def page(self, page):
        urlQuery = Url.all()
        urlQuery.order("-creationDate")
        return urlQuery.fetch(10, (page - 1) * 10)
    
    def output(self, list = []):
        return

class UrlHelpers:
    def CreateAndStoreUrl(self, action = ""):
           
        action = re.sub("^http%3A%2F%2F", "", action)
        action = re.sub("^http%3A//", "", action)
        action = re.sub("^http://", "", action)        
        action = re.sub("javascript:", "", action)
        action = re.sub("<script>(.*?)</script>", "", action)
        
        action = urllib.unquote(action)
        
        #Attempt to get the url from the database.
        url = Url.gql("WHERE url = :1", action).get();
        output = ""
        
        if url:
            output = ""
        else:
            url = Url() 
            url.url = action
            url.count = 0
            url.creationDate = datetime.datetime.now()
            url.put()

        converter = Base62to10.BaseNConverter()
        return converter.base10ToN(url.key().id(),62) # get the internal id of the key.

class Redirector(webapp.RequestHandler):
    def get(self, action = ""):
        #Get an instance of the key.
        converter = Base62to10.BaseNConverter()
        number = converter.baseNto10(action, 62)

        url = Url.get_by_id(number)
        
        if url is None:
            path = os.path.join(os.path.dirname(__file__), 'error.html')
            newUris = NewUrls()
            topUris = TopUrls()
            self.response.out.write(template.render(path, {"top": topUris.list(), "new": newUris.list()}));
        else:
            #The action is the id of the page.  Get it out of the file store.
            url.count = url.count + 1
            if url.creationDate is None:
                url.creationDate = datetime.datetime.now()
            url.put() # store the update.
            if re.match("eweri.com/([a-zA-Z0-9]+)", url.url) == True:
                self.redirect("http://eweri.com") # Any link to another eweri url will just point back to here
            else:
                self.redirect("http://" + url.url)

class UrlStorer(webapp.RequestHandler):
    def get(self, action = ""):       
        #Validate the input.
        if action != "" and self.request.query_string != "":
            action = action + "?" + self.request.query_string
            
        action = self.request.get("uri", action)
        urlHelper = UrlHelpers()
        
        action = urllib.unquote(action)
        
        action = self.request.get("uri", action)      
        
        keyId = urlHelper.CreateAndStoreUrl(action)
        
        newUris = NewUrls()
        topUris = TopUrls()
        
        path = os.path.join(os.path.dirname(__file__), 'eweriResult.html')
        self.response.out.write(template.render(path, {'url': "http://eweri.com/" + keyId, "new": newUris.list(), "top": topUris.list()}));

class ApiUrlStorer(webapp.RequestHandler):
    def get(self, action = ""):
        #Validate the input.
         #Validate the input.
        if action != "" and self.request.query_string != "":
            action = action + "?" + self.request.query_string
        action = self.request.get("uri", action)
        action = re.sub("^http%3A%2F%2F", "", action)
        action = re.sub("^http%3A//", "", action)
        action = re.sub("^http://", "", action)        
        action = re.sub("javascript:", "", action)
        action = re.sub("<script>(.*?)</script>", "", action)
        
        action = urllib.unquote(action)
        
        #Attempt to get the url from the database.
        url = Url.gql("WHERE url = :1", action).get();
        output = ""
        
        if url:
            output = ""
        else:
            url = Url() 
            url.url = action
            url.count = 0
            url.creationDate = datetime.datetime.now()
            url.put()

        converter = Base62to10.BaseNConverter()
        keyId = converter.base10ToN(url.key().id(),62) # get the internal id of the key.
        
        self.response.out.write("http://eweri.com/" + keyId);



class ApiBatchUrlStorer(webapp.RequestHandler):
    def post(self, action = ""):
        #Validate the input.
        urlXml = self.request.POST.get("urls")

        urls = re.findall('<url>(.+?)</url>', urlXml)

        urlHelper = UrlHelpers()

        self.response.out.write("<urls>")
                
        for url in urls:
            keyId = urlHelper.CreateAndStoreUrl(url)
            self.response.out.write("<url><long>" + url + "</long><short>http://eweri.com/" + keyId + "</short></url>");
        self.response.out.write("</urls>")

class ApiLatestUrlLister(webapp.RequestHandler):
    def get(self, action = "1"):
        page = int(action)
        urls = NewUrls()
        
        prev = page - 1
        next = page + 1
        
        if page == 1:
            prev = 1
        
        for url in urls.page(page):
            self.response.out.write(url.url + "\n")

class Index(webapp.RequestHandler):
    def get(self, action = ""):        
        newUris = NewUrls()
        topUris = TopUrls()
                
        path = os.path.join(os.path.dirname(__file__), 'eweri.html')
        self.response.out.write(template.render(path, {"new": newUris.list(), "top": topUris.list()}))

class NewPage(webapp.RequestHandler):
    def get(self, action=""):
        page = int(action)
        newUris = NewUrls()
        path = os.path.join(os.path.dirname(__file__), 'newList.html')
        
        prev = page - 1
        next = page + 1
        
        if page == 1:
            prev = 1
            
        self.response.out.write(template.render(path, {"new": newUris.page(page), "prev":  prev, "next": next}))
        
class TopPage(webapp.RequestHandler):
    def get(self, action=""):
        page = int(action)
        topUris = TopUrls()
        
        prev = page - 1
        next = page + 1
        
        if page == 1:
            prev = 1
        
        path = os.path.join(os.path.dirname(__file__), 'topList.html')
        self.response.out.write(template.render(path, {"top": topUris.page(page), "prev": prev, "next": next}))


def main():
    application = webapp.WSGIApplication([(r'/add/(.*)', UrlStorer), (r'/api/list/recent/(.*)', ApiLatestUrlLister), (r'/api/batchadd', ApiBatchUrlStorer), (r'/api/add/(.*)', ApiUrlStorer), ('/', Index), (r'/new/(\d+)', NewPage), (r'/top/(\d+)', TopPage), (r'/(.+)', Redirector)], debug=True)
    wsgiref.handlers.CGIHandler().run(application);

if __name__ == '__main__':
  main()