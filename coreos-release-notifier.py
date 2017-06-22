#!/usr/bin/python

import urllib, json, sys, getopt, threading, urllib, urllib2
from datetime import datetime
from dateutil import parser

def main(argv):
   feed_url = 'https://coreos.com/releases/releases.json'
   webhook_url = ''
   polling_frequency = 60
   image_version_url = 'https://stable.release.core-os.net/amd64-usr/current/version.txt'

   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'coreos-release-notifier.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'coreos-release-notifier.py -i <CoreOS Releases Feed URL> -c <CoreOS Image Version TXT URL> -o <Slack Webhook URL> -p <polling period in seconds>'
         sys.exit()
      elif opt in ("-i"):
         feed_url = arg
      elif opt in ("-p"):
         polling_frequency = arg
      elif opt in ("-c"):
         image_version_url = arg
      elif opt in ("-o"):
         webhook_url = arg

   # check the values of required config options
   if webhook_url == '':
       print 'Webhook URL was not specified, cannot proceed'
       sys.exit()

   check_feed(feed_url, image_version_url, webhook_url, polling_frequency, '')

def check_feed(feed_url, image_version_url, webhook_url, polling_frequency, latest_release_id):
   # retrieve the version of the latest image
   image_attributes = {}
   for line in urllib.urlopen(image_version_url):
       name, var = line.partition("=")[::2]
       image_attributes[name.strip()] = var.strip()

   if latest_release_id == '' or image_attributes['COREOS_VERSION'] != latest_release_id:
       # retrieve the JSON-formatted feed
       response = urllib.urlopen(feed_url)
       data = json.loads(response.read())

       if image_attributes['COREOS_VERSION'] in data:
           print "Sending release details to Slack"
           latest_release_id = image_attributes['COREOS_VERSION']
           parsed_date = parser.parse(data[latest_release_id]['release_date'])
           slack_data = json.dumps({"attachments":[{"color": "warning", "title": ("CoreOS %s" % latest_release_id), "title_link": "https://coreos.com/releases/","text": data[latest_release_id]['release_notes'], "ts": parsed_date.strftime('%s')}]}, sort_keys=True)
           headers = {'Content-Type': 'application/json'}
           req = urllib2.Request(webhook_url, slack_data, headers)
           response = urllib2.urlopen(req)
   else:
       print "No changes"
   threading.Timer(polling_frequency, check_feed, [feed_url, image_version_url, webhook_url, polling_frequency, latest_release_id]).start()

if __name__ == "__main__":
   main(sys.argv[1:])
