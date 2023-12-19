#! /usr/bin/python3
#
# @(!--#) @(#) inbox.py, sversion 0.1.0, fversion 008, 19-december-2023
#
# a CGI script to display the contents of an inbox
# as stored using the smua (simple mail user agent) program
# via a .forward file
#

########################################################################

#
# imports
#

import sys
import os
import html
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

########################################################################

#
# constants
#

DEFAULT_USERNAME = 'andyc'

ETC_PASSWD = '/etc/passwd'

########################################################################

def unixbasename(filename, extension):
    lenfilename = len(filename)

    lenext = len(extension)

    if lenext < lenfilename:
        if filename[-lenext:] == extension:
            filename = filename[0:lenfilename-lenext]

    return filename

########################################################################

def showerror(errortext):
    print('<html>')
    print('<head>')
    print('<title>Error!</title>')
    print('</head>')
    print('<body>')
    print('<h1>Error: {}</h1>'.format(html.escape(errortext)))
    print('</body>')
    print('</html>')

    return

########################################################################

def extractusername():
    try:
        scriptname = os.environ['SCRIPT_FILENAME']
    except KeyError:
        scriptname = ''

    username = ''

    if scriptname != '':
        pieces = scriptname.split('/')

        if len(pieces) >= 2:
            lastbutone = pieces[-2]

            if len(lastbutone) >= 2:
                if lastbutone[0] == '~':
                    lastbutone = lastbutone[1:]

                    if lastbutone.islower():
                        username = lastbutone

    return username

########################################################################

def etcpasswd(username):
    try:
        f = open(ETC_PASSWD, 'r', encoding='utf-8')
    except IOError:
        return '', ''

    homedir = ''
    fullname = ''

    for line in f:
        pieces = line.split(':')

        if len(pieces) >= 7:
            if pieces[0] == username:
                homedir = pieces[5]
                fullname = pieces[4]
                fullname = fullname.split(',')[0]
                break

    f.close()

    return homedir, fullname

########################################################################

def cleanupdatetime(datetime):
    pieces = datetime.split()

    for i in range(0, 2):
        lastpiece = pieces[-1]

        if (lastpiece[0] == '(') or (lastpiece[0] == '+'):
            pieces = pieces[:-1]

    return " ".join(pieces)

########################################################################

def unpackmessage(msgfilename):
    msg = {}

    try:
        msgfile = open(msgfilename, 'r', encoding='utf-8')
    except FileNotFoundError:
        msg['status'] = 'error'
        return msg

    headerlines = []
    bodylines = []

    inheader = True

    subjectline = ''
    dateline = ''
    fromline = ''

    for line in msgfile:
        line = line.rstrip()

        if inheader:
            if line == '':
               inheader = False
               continue

        if inheader:
            headerlines.append(line)

            if subjectline == '':
                if line.startswith('Subject: '):
                    subjectline = line[9:].strip()
 
            if dateline == '':
                if line.startswith('Date: '):
                    dateline = cleanupdatetime(line[6:])
 
            if fromline == '':
                if line.startswith('From: '):
                    fromline = line[6:]
        else:
            bodylines.append(line)

    msgfile.close()

    if subjectline == '':
        subjectline = 'No subject specified'

    msg['status'] = 'ok'
    msg['filename'] = msgfilename
    msg['header'] = headerlines
    msg['body'] = bodylines
    msg['subject'] = subjectline
    msg['date'] = dateline
    msg['from'] = fromline

    return msg

########################################################################

def getmsglist():
    msglist = []

    for f in os.listdir('.'):
        if len(f) > 10:
            if f.endswith('.lck'):
                msgfilename = f[:-4]
                msg = unpackmessage(msgfilename)
                if msg['status'] == 'ok':
                    msglist.append(msgfilename)

    msglist.sort(reverse=True)

    return msglist

########################################################################

def displaysummary(msg):
    global pagename

    print('<tr>')


    print('<td class="col1">')
    print('<a href="{}?action=message&msgid={}">'.format(pagename, msg['filename']))
    print(msg['from'])
    print('</a>')
    print('</td>')

    print('<td class="col2">')
    print('<a href="{}?action=message&msgid={}">'.format(pagename, msg['filename']))
    print(msg['subject'])
    print('</a>')
    print('</td>')

    print('<td class="col3">')
    print('<a href="{}?action=message&msgid={}">'.format(pagename, msg['filename']))
    print(msg['date'])
    print('</a>')
    print('</td>')

    print('<td class="col4">')
    print('<a href="{}?action=delete&msgid={}"><img src="trash.png"></a>'.format(pagename, msg['filename']))
    print('</td>')

    print('</tr>')

    return

########################################################################

def displayinbox():
    msglist = getmsglist()


    if len(msglist) == 0:
        print('<p class="nomessages">')
        print('No messages')
        print('</p>')
    else:
        print('<table>')

        print('<tr>')
        print('<th class="col1">From</th>')
        print('<th class="col2">Subject</th>')
        print('<th class="col3">Date</th>')
        print('<th class="col4"></th>')
        print('</tr>')

        for msgfilename in msglist:
            msg = unpackmessage(msgfilename)
            if msg['status'] == 'ok':
                displaysummary(msg)

        print('</table>')

    return

########################################################################

def displaymessage(msgfilename):
    global pagename

    msg = unpackmessage(msgfilename)

    if msg['status'] != 'ok':
        print('<p class="error">')
        print('*** Message format not valid ***')
        print('</p>')
        return


    print('<p class="msgheader">')

    linecount = 0

    for line in msg['header']:
        linecount += 1
        if linecount > 1:
            print('<br>')
        print(line)
        if linecount == 1:
            print('<a href="{}?action=delete&msgid={}"><img class="floatright" src="trash.png"></a>'.format(pagename, msgfilename))

    print('</p>')

    print('<p class="msgbody">')

    linecount = 0

    for line in msg['body']:
        linecount += 1
        if linecount > 1:
            print('<br>')
        print(line)

    print('</p>')

    return

########################################################################

def main():
    global pagename
    global pagebasename

    username = extractusername()

    if username == '':
        username = DEFAULT_USERNAME

    homedir, fullname = etcpasswd(username)

    smuadir = homedir + '/.smua'

    try:
        os.chdir(smuadir)
    except FileNotFoundError:
        showerror('No "{}" directory'.format(smuadir))
        return 1

    pagetitle = 'Inbox'

    form = cgi.FieldStorage()

    actionfield = form.getlist("action")

    if len(actionfield) == 0:
        action = 'main'
    else:
        action = actionfield[0]

    if action == 'delete':
        msgidfield = form.getlist("msgid")

        if len(msgidfield) > 0:
            msgid = msgidfield[0]

            try:
                os.remove(msgid)
            except FileNotFoundError:
                pass

            try:
                os.remove(msgid + '.lck')
            except FileNotFoundError:
                pass

            action = 'main'

    if action == 'message':
        msgidfield = form.getlist("msgid")
        if len(msgidfield) != 1:
            action = 'main'
        else:
            msgfilename = msgidfield[0]

    print('Content-type: text/html; charset=utf-8')
    print('')

    print('<!doctype html>')

    print('<html>')

    print('<head>');

    print('<title>{} - {} ({})</title>'.format(html.escape(pagetitle), html.escape(fullname), html.escape(username)))

    print('<meta charset="utf-8">')

    if action == 'main':
        print('<meta http-equiv="refresh" content="5">')

    print('<link rel="stylesheet" type="text/css" href="{}.css">'.format(pagebasename))

    print('</head>');

    print('<body>')

    print('<h1><a href="{}">{} for {} ({})</a></h1>'.format(pagename, html.escape(pagetitle), html.escape(fullname), html.escape(username)))

    print('<hr>')

    if action == 'main':
        displayinbox()
    elif action == 'message':
        displaymessage(msgfilename)
    else:
        print('<p class="error">')
        print('Action "{}" unsupported'.format(action))
        print('</p>')

    print('<hr>')

    print('</body>')

    print('</html>')

    return 0

########################################################################

pagename = os.path.basename(sys.argv[0])

pagebasename = unixbasename(pagename, '.py')

sys.exit(main())

# end of file
