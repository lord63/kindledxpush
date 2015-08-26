#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sqlite3
import sys
import re
import os
import json
import HTMLParser

import requests
from bs4 import BeautifulSoup
from terminal import Command

from kindlepush import __version__


# Set default encoding from ascii to utf-8
reload(sys)
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding('utf-8')

# User-agent is necessary, or it'll occur `KeyError: 'data' `.
GLOBAL_SESSION = requests.Session()
GLOBAL_SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                               x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})


def unescape(raw_title):
    """unescape html character, to support chinese in title"""
    html_parser = HTMLParser.HTMLParser()
    if re.search(r'&.*;', raw_title):
        return html_parser.unescape(raw_title)
    else:
        return raw_title


def get_hidden_form_data(page):
    '''Get hidden form data from the page after you click the signin button

    Those data are needed to post to sign in.'''
    hidden_form_data = dict()
    input_tags = page.findAll('input', type='hidden')
    for tag in input_tags:
        hidden_form_data[tag['name']] = tag['value']
    return hidden_form_data


def login(config):
    '''To login in to amazom.com

    The long url is the 'sign in' botton, the short is the 'sign in our
    secure sever' botton.'''

    print 'Login...'
    login_url = ('https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc'
                 '_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.n'
                 'et%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%'
                 '2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openi'
                 'd.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net'
                 '%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2'
                 'Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.r'
                 'eturn_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhom'
                 'e%3Fie%3DUTF8%26ref_%3Dgno_signin')
    login_post_url = 'https://www.amazon.com/ap/signin'
    login_page = BeautifulSoup(GLOBAL_SESSION.get(login_url).text)
    data = get_hidden_form_data(login_page)
    data.update({'email': config['email'], 'password': config['password']})
    GLOBAL_SESSION.post(login_post_url, data)


def get_contents(config):
    """get all the information of docs in our kindle library"""
    url = ('https://www.amazon.com/gp/digital/fiona/manage/features/'
           'order-history/ajax/queryPdocs.html')
    request = GLOBAL_SESSION.post(url, {'offset': 0, 'count': config['count'],
                                        'contentType': 'Personal Document',
                                        'queryToken': 0, 'isAjax': 1})
    return [
        {'category': item['category'], 'contentName': item['asin'],
         'title': item['title']} for item in request.json()['data']['items']
        ]


def get_device_id():
    """automatically get the device id used when sending your docs"""
    request = GLOBAL_SESSION.post(
        'https://www.amazon.com/mn/dcw/myx/ajax-activity',
        data={'data': '{"param": {"GetDevices": {}}}'})
    device_id = request.json()['GetDevices']['devices'][0]['deviceAccountId']
    return device_id


def get_pending_deliveries():
    """get pending deliveries"""
    request = GLOBAL_SESSION.post(
        'https://www.amazon.com/mn/dcw/myx/ajax-activity',
        data={'data': '{"param": {"GetTodo": {}}}'})
    titles = [unescape(item['title']) for item in
              request.json()['GetTodo']['todoItems']]
    return titles


def deliver_content(content):
    """the function to deliver one doc"""
    url = ('https://www.amazon.com/gp/digital/fiona/content-download/'
           'fiona-ajax.html/ref=kinw_myk_ro_send')
    content.update({'isAjax': '1', 'deviceID': get_device_id()})
    request = GLOBAL_SESSION.post(url, content)
    # Whether successfully delivered it or not
    assert request.json()['data'] == 1


def deliver_all(contents, database):
    '''Deliver all the contents which haven't been delivered before

    Once delivered it, save it's asin in database.'''

    print 'Delivering'
    cursor = database.cursor()

    def content_in_database(content):
        """check whether a doc has been delivered or not"""
        try:
            cursor.execute('select * from content where name = "%s"' % content)
        except sqlite3.OperationalError:
            cursor.execute('create table content (name text)')
            return False
        else:
            return False if cursor.fetchone() is None else True

    contents = filter(lambda x: not content_in_database(x['contentName']),
                      contents)
    if not contents:
        sys.exit('All the docs in your library have been delivered'
                 'to your kindle')
    for content in contents:
        try:
            deliver_content(content)
            print 'delivering ' + unescape(content['title'])
        except Exception, error:
            logging.error(repr(error))
            print repr(error)
        else:
            cursor.execute('insert into content values ("%s")' %
                           content['contentName'])
            print 'Done. Save to database.'
            logging.info('delivered ' + unescape(content['title']))
    database.commit()


def main():
    command = Command('kindlepush',
                      'automatically deliver your docs to your kindle',
                      version=__version__)
    command.option('-c, --count [count]', 'the count of the docs to deliver')

    try:
        with open(os.path.join(sys.path[0], 'kindlepush_config.json')) as f:
            config = json.load(f)
    except IOError:
        sys.exit("Check your config file in {0}".format(sys.path[0]))

    @command.action
    def read(number=config['number']):
        """
        read the log file

        :param number: the count of days
        :option number: -n, --number [number]
        """
        file_path = os.path.join(config['directory'], 'kindlepush.log')
        os.system('tail -n {0} {1}'.format(number, file_path))

    @command.action
    def pending():
        """
        get pending deliveries
        """
        login(config)
        titles = get_pending_deliveries()
        print "Pending Deliveries:"
        for title in titles:
            print '\t{0}'.format(title)

    command.parse()

    logging.basicConfig(
        filename=os.path.join(config['directory'], 'kindlepush.log'),
        level='INFO',
        format='%(asctime)s [%(levelname)s] %(message)s')
    # Disable unwanted log message from the requests library
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    # Connect to the database lying the directory specified in the config
    database = sqlite3.connect(os.path.join(config['directory'],
                                            'kindlepush.db'))

    # overwrite the value of count if user has specified it
    if command.count:
        config['count'] = command.count

    if ('read' not in sys.argv) and ('pending' not in sys.argv):
        try:
            login(config)
            deliver_all(get_contents(config), database)
        except KeyError:
            print 'KeyError, check your config file please.'
        except requests.exceptions.ConnectionError:
            print 'Check your network please.'
