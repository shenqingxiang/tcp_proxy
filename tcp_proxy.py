# -*- coding: utf-8 -*-
# tcp mapping created by shenqingxiang

""" TCP protocol transfer

"""

import socket
import threading


# 远端目的IP 字符
REMOTE_IP = ''
# 远端目的端口 数字
REMOTE_PORT = 1521
# 本地绑定IP，默认
LOCAL_IP = '0.0.0.0'
# 本地绑定端口
LOCAL_PORT = 8526
# 接收数据缓存大小
PKT_BUFF_SIZE = 1024 * 5


class Transfer:

    def __init__(self):
        pass

    # 单向流数据传递
    def tcp_mapping_worker(self, conn_receiver, conn_sender):
        while True:
            try:
                data = conn_receiver.recv(PKT_BUFF_SIZE)
            except Exception as e:
                self.send_log('Event: Connection closed.')
                break

            if not data:
                self.send_log('Info: No more data is received.')
                break

            try:
                conn_sender.sendall(data)
            except Exception:
                self.send_log('Error: Failed sending data.')
                break

            # send_log('Info: Mapping data > %s ' % repr(data))
            self.send_log('Info: Mapping > %s -> %s > %d bytes.' % (
                conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))

        conn_receiver.close()
        conn_sender.close()

        return

    # 端口映射请求处理
    def tcp_mapping_request(self, local_conn, remote_ip, remote_port):
        remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            remote_conn.connect((remote_ip, remote_port))
        except Exception:
            local_conn.close()
            self.send_log('Error: Unable to connect to the remote server.')
            return

        threading.Thread(target=self.tcp_mapping_worker, args=(local_conn, remote_conn)).start()
        threading.Thread(target=self.tcp_mapping_worker, args=(remote_conn, local_conn)).start()

        return

    # 调试日志封装
    def send_log(self, content):
        print content
        return

    # 端口映射函数
    def tcp_mapping(self, remote_ip, remote_port, local_ip, local_port):
        local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_server.bind((local_ip, local_port))
        local_server.listen(5)

        self.send_log('Event: Starting mapping service on ' + local_ip + ':' + str(local_port) + ' ...')

        while True:
            try:
                (local_conn, local_addr) = local_server.accept()
            except KeyboardInterrupt:
                local_server.close()
                self.send_log('Event: Stop mapping service.')
                break

            threading.Thread(target=self.tcp_mapping_request, args=(local_conn, remote_ip, remote_port)).start()

            self.send_log('Event: Receive mapping request from %s:%d.' % local_addr)
        return

# 主函数
if __name__ == '__main__':
    t = Transfer()
    t.tcp_mapping(REMOTE_IP, REMOTE_PORT, LOCAL_IP, LOCAL_PORT)

