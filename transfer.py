#!/usr/bin/env/python
#-*- coding: utf-8 -*-

import posterous
import time

import oauth2 as oauth
import urlparse
import urllib

p_api = posterous.API('POSTEROUS EMAIL', 'POSTEROUS PASSWORD')

# Tumblr OAuth stuff
consumer_key = "CONSUMER KEY HERE"
consumer_secret = "CONSUMER SECRET HERE"

endpoint = "http://api.tumblr.com"
request_token_url = "http://www.tumblr.com/oauth/request_token"
access_token_url = "http://www.tumblr.com/oauth/access_token"
authorize_url = "http://www.tumblr.com/oauth/authorize"
post_url = "http://api.tumblr.com/v2/blog/BLOG URL HERE/post"

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

resp, content = client.request(request_token_url, "GET")
if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

request_token = dict(urlparse.parse_qsl(content))

print "Request Token:"
print "    - oauth_token        = %s" % request_token['oauth_token']
print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
 
 
# Step 2: Redirect to the provider. Since this is a CLI script we do not 
# redirect. In a web application you would redirect the user to the URL
# below.

print "Go to the following link in your browser:"
print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
print 

# After the user has granted access to you, the consumer, the provider will
# redirect you to whatever URL you have told them to redirect to. You can 
# usually define this in the oauth_callback argument as well.
accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
oauth_verifier = raw_input('What is the PIN? ')

# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the 
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this 
# access token somewhere safe, like a database, for future use.
token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
access_token = dict(urlparse.parse_qsl(content))

print "Access Token:"
print "    - oauth_token        = %s" % access_token['oauth_token']
print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
print
print "You may now access protected resources using the access tokens above." 

token = oauth.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])

p_sites = p_api.get_sites()

for site in p_sites:
  if site.name == 'NAME OF SITE YOU WANT TO TRANSFER':
    id = site.id
    
for p_post in p_api.read_posts(site_id=id, num_posts=175):
  
  
  #print "Title = {}" .format(p_post.title.encode('ascii', 'ignore'))
  #print "Body = {}" .format(p_post.body.encode('ascii', 'ignore'))
  #print "Link = {}" .format(p_post.link.encode('ascii', 'ignore'))
  #print "Date = {}" .format(p_post.date)
  
  params = {
    "oauth_version": "1.0",
    "oauth_nonce": oauth.generate_nonce(),
    "oauth_timestamp": int(time.time()),
    "type": "text",
    "date": p_post.date,
    "title": p_post.title,
    "body": p_post.body,
  }
    
  params['oauth_token'] = token.key
  params['oauth_consumer_key'] = consumer.key
    
  req = oauth.Request(method="POST", url=post_url, parameters=params)
  signature_method = oauth.SignatureMethod_HMAC_SHA1()
  req.sign_request(signature_method, consumer, token)
  result = urllib.urlopen(post_url, req.to_postdata())
  print result    
  
