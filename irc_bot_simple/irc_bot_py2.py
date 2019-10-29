__author__ = 'mikroman'



import socket
import urllib
import optparse
from random import randint

server = "irc.freenode.net"
test_channel="#mytestchannel"
webpage = 'http://pages.cs.wisc.edu/~ballard/bofh/bofhserver.pl'
channel = "" # #reddit-sysadmin
botnick = "" #default Excuse-O-Bots

unknownQuestions = ['I do not understand this.','This is not a legit command.','Please rephrase your inquiry.','Command unknown.','Failure while parsing. Repeat command.']

def get_excuse(size):
    data = []
    for i in range(0,size):
        socket = urllib.urlopen(webpage)
        html = socket.readlines()
        socket.close()
        data.append(parse_html(html))

    return data

def parse_html(html):
    line = html[1]
    return line[198:]


def ping():
    ircsock.send("PONG :pingis\n")


def sendmsg(chan, msg):
    ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")


def join(chan):
    ircsock.send("JOIN " + chan + "\n")


def part(msg):
    ircsock.send("PART " + channel + " :" + msg + "\n")


def action(action,nick):
    ircsock.send("PRIVMSG " + channel + " :\001ACTION "+ action+" "+ nick + "\001\n")


def parse_msg(ircmsg):
    msg = ircmsg
    ircmsg = ircmsg[ircmsg.index("PRIVMSG"):]
    print ircmsg

    if ircmsg.find("excuse") != -1:
        print ircmsg
        sendmsg(channel,excuses.pop(0))

    elif ircmsg.find("help") != -1:
        print ircmsg
        sendmsg(channel, "I am a generator of high-tech excuses. Call me with " + botnick + ": <command>. Commands: excuse, help, who are you, hug me")

    elif ircmsg.find("who are you") != -1:
        sendmsg(channel, "I am " + botnick +", your robotic overlord. Just kidding, a shitty Python script written by MikroMan. Type \" Excuse-O-Bot help\" for more commands")

    elif ircmsg.find("hug me") != -1:
        msg_nick = msg[1:msg.index("!")]
        action("hugs",msg_nick)

    else:
        sendmsg(channel,unknownQuestions[randint(0,len(unknownQuestions))])


if __name__ == "__main__":

    #argument parser for command line aguments
    parser = optparse.OptionParser()

    #defaults to Excuse-O-Bot at #reddit-sysadmin
    parser.add_option('-n','--nick',action="store", dest="nick", default="Excuse-O-Bot",help="Nickname of your bot")
    parser.add_option('-c','--channel',action="store", dest="chan", default="#reddit-sysadmin",help="channel to join")
    parser.add_option('-p','--pass',action="store", dest="passwd",help="password for your bot")

    options, args = parser.parse_args()

    botnick = options.nick
    password = options.passwd
    channel = options.chan
    print "Logging in as " + botnick+" @ "+channel

    #exit if no password given
    if options.passwd is None:
        print "No password provided"
        print "Exiting"
        exit(-1)

    excuses = get_excuse(30)
    print "Getting first quotes..."
    #note: removed requiring quotes from main loop
    #due to lockups. Need a solution ASAP. In the meantime, raise range for more quotes.


    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((server, 6667)) #  connect to the server
    ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :MikroMan's Excuse-O-Bot\n") # user authentication
    ircsock.send("NICK "+ botnick +"\n") #  assign the nick

    ircsock.send("PRIVMSG NICKSERV :IDENTIFY "+password+"\r\n")

    join(channel)
    print "Joined " + channel

    while 1:
        ircmsg = ircsock.recv(2048) # receive data from the server
        ircmsg = ircmsg.strip('\n\r')

        if ircmsg.find(botnick) != -1 and ircmsg.find("PRIVMSG") != -1:
            parse_msg(ircmsg)

        if ircmsg.find("PING :") != -1: #respond to ping
            ping()
        if len(excuses) < 2:
            sendmsg(channel,"Please stand by while I retrieve more excuses for you.")
            part("Loading more excuses.")
            print "Left channel: "+channel
            excuses = get_excuse(30)
            print "Loaded more excuses."
            join(channel)
            print "Joined " + channel




