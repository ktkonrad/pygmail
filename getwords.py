#!/usr/bin/env python

import pygmail
import ConfigParser
import re
import datetime

CONFIG_FILE = 'gmail.cfg'
WORDS_FILE = 'words.txt'

sources = ['mw', 'dictionary', 'oxford', 'wordsmith']
emails = {'mw': 'word@m-w.com', 'dictionary': 'doctor@dictionary.com', 'oxford': 'wordoftheday.odo_us@oup.com', 'wordsmith': 'wsmith@wordsmith.org'}

def init():
    """create gmail object and login"""
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    username = config.get('gmail', 'username')
    password = config.get('gmail', 'password')
    gmail = pygmail.pygmail()
    gmail.login(username, password)
    return gmail

def get_word(gmail, source):
    email = emails[source]
    try:
        mail_id = gmail.get_mails_from(email)[-1] # most recent message
    except IndexError: # no mail from this source
        return ''
    function_for_source = eval('get_word_%s' % source)
    word = function_for_source(gmail, mail_id)
    return word

def get_word_mw(gmail, mail_id):
    subject = gmail.get_mail_subject_from_id(mail_id)
    m = re.match("Subject: ([\w '\-]+) - ", subject)
    if m:
        return m.groups(1)[0]
    else:
        return ''

def get_word_dictionary(gmail, mail_id):
    subject = gmail.get_mail_subject_from_id(mail_id)
    m = re.match("Subject: ([\w '\-]+):", subject)
    if m:
        return m.groups(1)[0]
    else:
        return ''


def get_word_oxford(gmail, mail_id):
    body = gmail.get_mail_body_from_id(mail_id)
    m = re.search("Your word for today is: <a[^>]*>([\w '\-]+)</a>", body)
    if m:
        return m.groups(1)[0]
    else:
        return ''

def get_word_wordsmith(gmail, mail_id):
    subject = gmail.get_mail_subject_from_id(mail_id)
    m = re.match("Subject: A.Word.A.Day--([\w '\-]+)", subject)
    if m:
        return m.groups(1)[0]
    else:
        return ''

def save_words(words):
    date = str(datetime.date.today())
    output = '%s,%s' % (date, ','.join(words))
    print output
    with open(WORDS_FILE, 'a') as f:
        print >> f, output

def main():
    gmail = init()
    words = [get_word(gmail, source) for source in sources]
    save_words(words)

if __name__ == '__main__':
    main()
