__author__ = 'mikroman'

import socket


class IrcBot:
    def __init__(self, server, channel, botnick, password):
        self.server = server
        self.channel = channel
        self.botnick = botnick
        self.password = password
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.ircsock.connect((server, 6667))
        self.irc_send(
            "USER " + botnick + " " + botnick + " " + botnick + " :MikroMan's Excuse-O-Bot\n")  # user authentication
        self.irc_send("NICK " + botnick + "\n")  # assign the nick

        self.irc_send("PRIVMSG NICKSERV :IDENTIFY " + password + "\r\n")

        self.irc_send("JOIN " + test_channel + "\n")

    def irc_send(self, msg):
        self.ircsock.send(encode(msg))

    # msg methods
    def part(self, quit_msg):
        self.irc_send("PART " + self.channel + " :" + quit_msg + "\n")

    def ping(self):
        self.irc_send("PONG :pingis\n")


    def send_msg_to_channel(self, msg):
        self.irc_send("PRIVMSG " + self.channel + " :" + msg + "\n")

    def process_msg(self, msg):
        if msg.find(encode("PING :")) != -1:  # respond to ping
            self.ping()
        else:
            print(msg)

def encode(msg):
    return bytes(msg, "UTF-8")


if __name__ == "__main__":
    server = "irc.freenode.net"
    test_channel = "#mytestchannel"

    botnick = "Excuse-O-Bot"  # default Excuse-O-Bot
    password = ""

    IRC = IrcBot(server, test_channel, botnick, password)
    IRC.start()

    while 1:
        buffer = IRC.ircsock.recv(2048)
        IRC.process_msg(buffer)






