#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""A simple guest book app that demonstrates the App Engine search API."""

import logging
from cgi import parse_qs
import re
import random
import os
import string
import urllib
from urlparse import urlparse
import base64
import datetime
import webapp2
from google.appengine.api import urlfetch

class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        # Log the error.
        
        logging.exception(exception)

        # Set a custom message.
        self.response.write('An error occurred. %s' % str(exception))

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)

def time_diff(start, end):
    return (end-start).microseconds

ping_url = "https://%s-dot-module-pong-dot-mq-cloud-prototyping-2.appspot.com"

time_f = '%Y-%m-%d %H:%M:%S:%f'
max_hops = 2

class MainPageHandler(BaseHandler):

   
    def get(self):

        #ping_to = url_to_fetch

        receive_time = datetime.datetime.now()

        try:
            counter_s = self.request.GET['hop_counter']
            counter = int(counter_s)
        except:
            counter = 0

        if counter > 0:

            #get hop metric

            #get originator
            req_originator_b64 = self.request.GET['originatorb64']
            req_originator = base64.urlsafe_b64decode(req_originator_b64.encode('utf8'))

            #get sent time
            sent_time_enc = self.request.GET['send_time']
            sent_time_enc = sent_time_enc.encode('utf8')
            #b64 decode
            sent_time_str = base64.urlsafe_b64decode(sent_time_enc)
            #2016-05-05 08:35:54.831770
            sent_time = datetime.datetime.strptime(sent_time_str, time_f)
            #calculate hop time
            diff = time_diff(sent_time, receive_time)
            last_hop_line = '<p>hop = %s, from = %s, to = %s, sent_time = %s, receive_time = %s, hop time (microsec) = %s,' % (counter, req_originator, self.request.host_url, sent_time, receive_time, diff)
        else:
            last_hop_line = '<p>'

        try:
            max_hops_passed_s = self.request.GET['maxhops']
            max_hops_passed = int(max_hops_passed_s)
        except:
            max_hops_passed = max_hops

        logging.info('counter = %s, max_hops = %s, last_hop_line = %s', counter, max_hops_passed, last_hop_line)

        if counter < max_hops_passed:            

            hop_counter = counter+1

            url = ping_url % hop_counter
                       
            url += '?'

            logging.info('next hop url = %s', url)
            
            #append hop counter
            url += '%s=%s' % ('hop_counter', counter+1)
            #append max hop counter
            url += '&'
            url += '%s=%s' % ('maxhops', max_hops_passed)
            #append send_time
            url += '&'
            enc_send_time = base64.urlsafe_b64encode(datetime.datetime.now().strftime(time_f))
            url += '%s=%s' % ('send_time', enc_send_time)
            #append originator url
            url += '&'
            originator_b64 = base64.urlsafe_b64encode(self.request.host_url)
            url += '%s=%s' % ('originatorb64', originator_b64)

            logging.info('fetch = %s', url)

            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    #append with this hop's metric
                    resp = last_hop_line + result.content
                    self.response.write(resp)
                else:
                    self.response.status = result.status_code
            except urlfetch.Error, e:
                logging.error("Caught exception fetching url {}".format(e))
        else:
            self.response.write(last_hop_line)


        


       



        

logging.getLogger().setLevel(logging.DEBUG)


app = webapp2.WSGIApplication(
    [('/.*', MainPageHandler)],
    debug=True)


