"""Setup for the package."""

from threading import Condition

from clock import get_clock
from connection_pool import ConnectionPool
from log import Log
from message_buffer import MessageBuffer
from message_processor import MessageProcessor
from operation_buffer import OperationBuffer
from operation_executor import OperationExecutor
from operation_sm import OperationStateMachine
from response_buffer import ResponseBuffer
from rpc_server import RPCServer
from socket_client import ClientSocket
from socket_server import ServerSocket
from utils import get_constants


def create_server(file_name):
    """Create the server."""

    cs = get_constants(file_name)
    get_clock()
    ips_addresses = cs.get_nodes()
    rpc_server_address = cs.get_server_address()
    server_socket_address = cs.get_server_socket()
    enter_cs = Condition()
    release_cs = Condition()
    log = Log()

    socket_connection_pool = ConnectionPool([])

    # print("This is the setup_server.py file")
    # print(cs.get_server_id())
    mb = MessageBuffer()
    rb = ResponseBuffer()
    ob = MessageBuffer()

    mp = MessageProcessor(mb, ob)
    mp.attach_connection_pool(socket_connection_pool)
    mp.set_cs_condition(enter_cs)

    op = OperationExecutor(ob)
    op.attach_connection_pool(socket_connection_pool)
    op.set_cs_condition(enter_cs)
    op.set_additem_condition(release_cs)
    op.set_log(log)

    osm = OperationStateMachine(rb)
    osm.set_additem_condition(release_cs)
    osm.set_log(log)

    # #print(ips_addresses)
    ss = ServerSocket(server_socket_address, mb)
    # print("server socket iniciado")
    sc = ClientSocket(ips_addresses, mb)
    # print("client socket iniciado")
    rpc = RPCServer(rpc_server_address, mb, rb, socket_connection_pool)
    # print("rpc server iniciado")

    sc.start(socket_connection_pool)
    ss.start(socket_connection_pool)

    rpc.start()
    mp.start()
    op.start()
    osm.start()

    rpc.join()
    op.join()
    mp.join()
    osm.join()


if __name__ == "__main__":
    create_server("serverips.txt")
