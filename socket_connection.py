"""Socket connection module."""

import functools
from queue import Queue
from threading import Condition, Thread

from critical_section_guard import get_csg
from message import Message
from message_buffer import MessageBuffer

HEADER = 1024
FORMAT = "utf-8"


@functools.total_ordering
class SocketConnection:
    """Socket connection class."""

    def __init__(self, conn, mb: MessageBuffer):
        """Initialize the socket connection."""
        self.conn = conn
        self.thread_incomming = Thread(target=self.handle_incomming)
        self.thread_outgoing = Thread(target=self.handle_outgoing)
        self.mb = mb
        self.out_queue = Queue()
        self.node_id = -1
        self.reply_condition: Condition | None = None

    def start(self):
        """Start the connection."""
        self.thread_incomming.start()
        self.thread_outgoing.start()

    def handle_incomming(self):
        """Handle the incoming messages."""
        conn = self.conn
        while True:
            res = conn.recv(HEADER).decode(FORMAT)
            res = res.strip()
            if res:
                res = Message.from_string(res)
                self.mb.put(res)

    def handle_outgoing(self):
        """Handle the outgoing messages."""

        while True:
            m = self.out_queue.get()
            m = str(m)

            self.send(m)

    def send(self, msg):
        """Send the message."""
        conex = self.conn
        message = msg.encode(FORMAT)
        msg_lenght = len(message)
        message += b" " * (HEADER - len(message))
        conex.send(message)

    def join(self):
        """Join the connection."""
        self.thread_incomming.join()
        self.thread_outgoing.join()

    def get_out_queue(self):
        """Get the out queue."""
        return self.out_queue

    def send_to_out_queue(self, message):
        """Send the message to the out queue."""
        self.out_queue.put(message)

    def __eq__(self, other):
        return self.node_id == other.node_id

    def __lt__(self, other):
        return self.node_id < other.node_id