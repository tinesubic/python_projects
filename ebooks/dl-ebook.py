import argparse
import io
import os
import shlex
import struct
import sys
import threading
from enum import Enum
from zipfile import ZipFile

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad

servers = {'irc.irchighway.net': '#ebooks', 'us.undernet.org': '#bookz'}


# Use Python 3
# Usage: Install IRC client lib with `pip install irc`
# Run `python ebooks.py --find Hitchhikers guide to the galaxy`
# Follow instructions


######## TODO list
# Add postprocessing to extract RAR archives
# TODO remove offers from offline users by default?
# TODO add arg to show offers even for offline users
# TODO add mechanism to detect search failure


class DownloadBookItem:
    """Extract information from raw book string"""

    def __init__(self, itemstring):
        # extract search string without filesize
        self.search_string = itemstring.split("::")[0].split('\r')[0]
        parts = itemstring.split(' ')

        # extract file host (user)
        self.host = parts.pop(0).replace('!', '')

        # some offers have integer order number??
        try:
            self.order_no = int(parts[0])
            parts.pop(0)
        except:
            pass
        self.name = None
        # extract author and title
        while len(parts) > 0 and not parts[0].startswith("::") and not parts[0].startswith('\r'):
            if self.name is None:
                self.name = parts.pop(0)
            else:
                self.name += " " + parts.pop(0)

        # skip any non relevan parts like \r------ or ::INFO::
        while len(parts) > 0 and ('-' in parts[0] or '::' in parts[0] or parts[0] == ""):
            parts.pop(0)

        # extract filesize if available
        if len(parts) > 0:
            self.size = " ".join(parts)
        else:
            self.size = "?"

    def stringify(self):
        return "{} - {} ({})".format(self.host, self.name, self.size)


class WaitingThread(threading.Thread):
    """Provides background thread task for ..... output while waiting"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()

    def run(self):
        while not self.stopped.wait(1):
            print(".", end='')


class EbookBot(irc.bot.SingleServerIRCBot):
    class ConnState(Enum):
        """Rudimentary state machine helper"""
        IDLE = 1
        FILELIST = 2
        FILE = 3

    def __init__(self, dir, channel, nickname, server, find, format, port=6667):
        self.server = server
        self.nick = nickname
        self.conn_state = self.ConnState.IDLE
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.received_bytes = 0
        self.file = None
        self.find = find
        self.dir = dir
        self.waiter = WaitingThread()
        self.users = []
        self.preferred_format = format

    def on_welcome(self, c, e):
        """After connecting to server, join a channel"""
        print("Connected to server `{}` as user `{}`".format(self.server, self.nick))
        c.join(self.channel)

    def _on_join(self, connection, event):
        """We get events for every user joined. If joined user is self, reset state and
        send search query"""
        if event.source.startswith(self.nick) and self.conn_state == self.ConnState.IDLE:
            print("Joined channel `{}`".format(self.channel))
            self.received_bytes = 0
            self.conn_state = self.ConnState.FILELIST
            self.connection.privmsg(self.channel, '@search {}'.format(self.find))
            self.waiter.start()
            print('Requested search for item `{}`'.format(self.find))

        super(EbookBot, self)._on_join(connection, event)

    def on_ctcp(self, connection, event):
        # check if received CTCP offer is requested file
        payload = event.arguments[1]
        parts = shlex.split(payload)
        if len(parts) != 5:  # TODO improve detection
            return
        command, filename, peer_address, peer_port, size = parts
        if command != "SEND":
            return

        print("\nReceived CTCP offer for file {}".format(filename))
        self.filename = os.path.basename(filename)

        self.file = b""  # reset file in memory
        peer_address = irc.client.ip_numstr_to_quad(peer_address)
        peer_port = int(peer_port)
        # start DCC download connection
        # TODO multiple connections?
        self.dcccon = self.dcc_connect(peer_address, peer_port, "raw")

    def on_dccmsg(self, connection, event):
        """Triggered when downloading files. Append received data to existing file data"""
        data = event.arguments[0]
        self.file += data
        self.received_bytes = self.received_bytes + len(data)
        self.dcccon.send_bytes(struct.pack("!I", self.received_bytes))

    def extract_filelist(self, input_zip, name):
        """Extract contents of search query result"""
        if input_zip is None:
            return []
        input_zip = ZipFile(io.BytesIO(input_zip))
        name = input_zip.namelist()[0]  # contains only one file (txt list)
        content = input_zip.read(name).decode('utf-8').split('\r\n')  # split into rows
        raw_items = list(filter(lambda x: x.startswith("!"), content))  # extract only offers (!nick)
        download_items = []
        for i in range(len(raw_items)):
            download_items.append(DownloadBookItem(raw_items[i]))  # parse into objects
        print("Unzipped filelist, found {} items.".format(len(download_items)))
        return download_items

    def select_file_from_list(self, filelist):
        """Shows offered book files and user prompt"""
        preferred = []
        others = []
        if self.preferred_format is not None:
            print("Showing preferred format first: {}".format(self.preferred_format))
            print('===============================================')
            for i in range(len(filelist)):
                if ".{}".format(self.preferred_format).upper() in filelist[i].stringify().upper():
                    preferred.append(filelist[i])
                else:
                    others.append(filelist[i])

        preferred.sort(key=lambda x: x.stringify().upper())
        others.sort(key=lambda x: x.stringify().upper())

        filelist = preferred + others

        for i in range(len(filelist)):
            item = filelist[i]
            print("[{}] - {} - {} ({})".format(i, item.host, item.name, item.size))

        answer = None
        while True:  # run until valid answer
            answer = input("Enter number of item to download:")
            try:
                answer = int(answer)
                if 0 <= answer < len(filelist):  # check if valid in range
                    if filelist[answer].host in self.channels[self.channel]._users:  # check if requested host is online
                        break
                    else:
                        print("User `{}` is currently not online. Please select another item.".format(
                            filelist[answer].host))
            except Exception as e:  # triggered if user enters garbage
                print("Invalid input value, please try again.")

        return filelist[answer]

    def process_file(self):
        """After download, parse file"""
        if self.filename.endswith(".zip"):  # if we detect a ZIP, extract files
            print("Detected ZIP archive, extracting contents.")
            input_zip = ZipFile(io.BytesIO(self.file))
            for name in input_zip.namelist():
                with open(os.path.join(self.dir, name), 'wb') as outfile:
                    outfile.write(input_zip.read(name))
        else:  # default case: just save file as is.
            print("No postprocess available, storing raw file.")
            with open(os.path.join(self.dir, self.filename), "wb") as outfile:
                outfile.write(self.file)

    def on_dcc_disconnect(self, connection, event):
        """When file is finished, execute user prompt or save file"""
        self.waiter.stopped.set()
        print()
        print('===============================================')
        print("Finished downloading {} ({} bytes).".format(self.filename, self.received_bytes))

        if self.conn_state == self.ConnState.FILELIST:  # if offer list received, extract and prompt user to choose
            print("Received list of available files for term `{}`".format(self.find))
            filelist = self.extract_filelist(self.file, self.filename)
            if len(filelist) > 0:  # reset state
                self.received_bytes = 0
                self.file = None
                self.conn_state = self.ConnState.FILE
                selected_file = self.select_file_from_list(filelist)
                print("Sending search term:", selected_file.search_string)
                self.waiter = WaitingThread()
                self.waiter.start()
                # send file request
                self.connection.privmsg(self.channel, selected_file.search_string)
            else:
                print("No files found")
        elif self.conn_state == self.ConnState.FILE:  # if we received a requested file, save it
            print("Saving file to {}".format(self.dir))
            self.process_file()
            print("Process finished, disconnecting.")
            self.connection.quit()
        else:
            print("Unknown status", self.conn_state)

    def on_disconnect(self, connection, event):
        print("Disconnected, exiting script")
        sys.exit(0)


def gen_nick(length=10):
    """Generates random nicknames"""
    import random, string
    return "".join(random.choice(string.ascii_uppercase) for i in range(length))


def parse_args():
    parser = argparse.ArgumentParser(description='IRC Ebook download helper script')
    parser.add_argument('--server', '-s', default='irc.irchighway.net', help="IRC hostname of server")
    parser.add_argument('--channel', '-c', default=None, type=str, help="IRC channel to use")
    parser.add_argument('--prefer-format', '-pf', default='mobi', type=str, help="IRC channel to use")
    parser.add_argument('--nick', '-n', default=gen_nick(), help="Bot nickname for connecting to IRC")
    parser.add_argument('--find', '-f', help="String to find")
    parser.add_argument('--dir', '-d', default='./downloads', help="Save directory")

    args = parser.parse_args()

    if args.find is None:
        print("Missing search term. See below for usage")
        parser.print_usage()
        sys.exit(1)

    if args.channel is None:
        args.channel = servers[args.server]

    return args


def prepare_folder(directory):
    print("Files will be downloaded to: {}".format(directory))
    os.makedirs(directory, exist_ok=True)


def main():
    args = parse_args()

    prepare_folder(args.dir)

    bot = EbookBot(server=args.server, nickname=args.nick, channel=args.channel, dir=args.dir, find=args.find,
                   format=args.prefer_format)
    bot.start()


if __name__ == "__main__":
    main()
