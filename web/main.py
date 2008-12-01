#!/usr/bin/env python

"""
This sites generates a books listings page based on data from a simple RESTful 
webservice. No admin interface is provided as that is part of another 
application. Currently the site provides HTML and JSON views but more are
planned for the future.
"""

# TODO: 404 page
# TODO: Exception handling for fetch
# TODO: RSS output
# TODO: RDF output
# TODO: Template
# TODO: Run through PyLint
# TODO: Write tests
# TODO: Adding logging

import os
import wsgiref.handlers
import simplejson

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import settings

# set to False for production
_DEBUG = True

class PageHandler(webapp.RequestHandler):
    "Expose HTML views of the data"
    def get(self):
        "Display the list of books as an HTML page."
        # first check if we have the list of books in the cache
        books = memcache.get("web_books")
        # if not then we need to create it
        if books is None:
            # get the JSON from the webservice
            response = fetch(settings.WEB_SERVICE_URL)
            json = response.content
            # convert the JSON to Python objects
            books = simplejson.loads(json)
            # store the python object in the cache for a specified time
            memcache.add("web_books", books, settings.CACHE_TIME)
        # seed the context with the list of books
        context = {
            "books": books
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))
        
class JsonHandler(webapp.RequestHandler):
    "Expose JSON views of the data"
    def get(self):
        "Display the list of books in JSON, mainly for machines"
        # first check if we have the list of books in the cache
        json = memcache.get("web_json")
        # if not then we need to create it
        if json is None:
            # get the JSON from the webservice
            response = fetch(settings.WEB_SERVICE_URL)
            json = response.content
            # store the JSON in the cache for a specified time
            memcache.add("web_json", json, settings.CACHE_TIME)
        # serve the response with the correct content type
        self.response.headers['Content-Type'] = 'application/json'        
        # write the json to the response
        self.response.out.write(json)

def application():
    "Separate application method for ease of testing"
    # register URL handlers
    return webapp.WSGIApplication([
        ('/', PageHandler),
        ('/books.json', JsonHandler),
    ], debug=False)

def main():
    "Run the application"
    wsgiref.handlers.CGIHandler().run(application())

if __name__ == '__main__':
    # if not imported then run the main() function
    main()