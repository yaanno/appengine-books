#!/usr/bin/env python

import os
import unittest
from webtest import TestApp, AppError

from google.appengine.api import urlfetch, mail_stub, apiproxy_stub_map, urlfetch_stub, user_service_stub, datastore_file_stub
from google.appengine.api.memcache import memcache_stub

from main import application, _email_new_book
from models import Book

class EmailTest(unittest.TestCase):
    def setUp(self):
                
        self.app = TestApp(application())
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())
        apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
        apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())
        apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())        
        stub = datastore_file_stub.DatastoreFileStub('temp', '/dev/null', '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
        
        os.environ['APPLICATION_ID'] = "temp"

    def test_sending_email(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
           title = "test",
           ident = "1",
           author = "author",
           notes = "",
           image = "http://example.com/image.gif",
           url = "http://example.com"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        # TODO: needs assertion
        _email_new_book(book)
            
if __name__ == "__main__":
    unittest.main()