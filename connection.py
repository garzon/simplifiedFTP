#!/usr/bin/env python2

import sys
import time
import socket
import select
import string
import re
import os

DEFAULT_TIMEOUT = 600

class Connection:
    def __init__(self, socket):
        self._socket = socket

        # Disable kernel TCP buffering
        #self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.buf = b''

    def __str__(self):
        return self.buf

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def disconnect(self):
        """Shut down and close the socket."""
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def recv(self, bufsize=10000, timeout=DEFAULT_TIMEOUT, dontraise=False):
        """Receive data from the remote end."""
        self._socket.settimeout(timeout)
        try:
            tmp = self.buf[:bufsize]
            self.buf = self.buf[len(tmp):]
            if bufsize > len(tmp):
                tmp += self._socket.recv(bufsize - len(tmp))
            return tmp
        except socket.timeout:
            if dontraise:
                return b''
            else:
                raise

    def recv_to_buf(self, bufsize=10000, timeout=DEFAULT_TIMEOUT, dontraise=False):
        if bufsize <= 0: return
        self._socket.settimeout(timeout)
        flag = True
        while flag:
            try:
                self.buf += self._socket.recv(bufsize)
                flag = False
            except socket.timeout:
                if not dontraise:
                    raise

    def getFromBuf(self, size):
        tmp = self.buf[:size]
        self.buf = self.buf[len(tmp):]
        return tmp

    def recvn(self, n, timeout=DEFAULT_TIMEOUT, dontraise=False):
        """Receive and Return exact n bytes"""
        self.recv_to_buf(bufsize=n-len(self.buf), timeout=timeout, dontraise=dontraise)
        return self.getFromBuf(n)

    def recv_until(self, keywords, timeout=DEFAULT_TIMEOUT):
        """Receive incoming data until one of the provided keywords is found."""
        notFound = 99999999
        index = notFound

        if isinstance(keywords, str):
            aim_keyword = keywords
            index = self.buf.find(keywords)
        elif isinstance(keywords, list):
            for keyword in keywords:
                tmp = self.buf.find(keyword)
                if tmp != -1 and tmp < index:
                    index = tmp
                    aim_keyword = keyword
        else:
            raise

        if index == notFound or index == -1:
            self.recv_to_buf()
            return self.recv_until(keywords, timeout)
        return self.getFromBuf(index+len(aim_keyword))

    def recv_until_match(self, regex, group=0, timeout=DEFAULT_TIMEOUT):
        """Receive incoming data until it matches the given regex."""
        if isinstance(regex, str):
            regex = re.compile(regex)
        match = regex.search(self.buf)
        if match == None:
            self.recv_to_buf()
            return self.recv_until_match(regex, timeout)
        match = match.group(group)
        index = self.buf.find(match)
        dummy = self.getFromBuf(index)
        return self.getFromBuf(len(match))

    def send(self, data):
        """Send all data to the remote end or raise an exception."""
        self._socket.sendall(data)

    def send_line(self, data):
        """Send all data to the remote end or raise an exception. Appends a \\n."""
        self.send(data + b'\n')

    def interact(self):
        """Interact with the remote end."""
        try:
            while True:
                sys.stdout.write(self.recv(timeout=.05, dontraise=True))
                available, _, _ = select.select([sys.stdin], [], [], .05)
                if available:
                    data = sys.stdin.readline()
                    self.send(data)
        except KeyboardInterrupt:
            return