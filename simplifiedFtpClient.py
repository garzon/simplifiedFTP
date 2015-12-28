import socket, thread, sys, connection, os, os.path

if len(sys.argv) <= 2:
    print 'Usage: python simplifiedFtpClient.py <host> <port>'
    exit()
    
def parse_cmd(cmd_string):
    STH_STRANGE = '!@#$%^&*&^%$#@'
    cmd_array = cmd_string.replace('::::', STH_STRANGE).split('::')
    cmd_array = [x.replace(STH_STRANGE, '::') for x in cmd_array]
    return (cmd_array[0], cmd_array[1:])

def send_bytes(c, bytes):
    c.send_line('OK::sending::%d' % len(bytes))
    c.send(bytes)
    
def client_handler(s, raw_string):
    c = connection.Connection(s)
    c.send_line('Welcome to Simplified FTP Server V1.0!')
    is_auth = False
    while True:
        c.send(('simplifiedFTP@' + os.getcwd() if is_auth else '') + '$ ')
        try:
            cmd_string = c.recv_until('\n')[:-1]
        except socket.timeout:
            print 'Connection from %s timeout, closed' % addr
            c.disconnect()
            break
        print 'Command From %s Received: %s' % (addr, cmd_string) 
        cmd, args = parse_cmd(cmd_string)
        if cmd == 'auth':
            if len(args) != 2:
                c.send_line('ERR::Invalid Parameters')
                continue
            if args != auth_settings:
                c.send_line('ERR::Invalid username/password')
                continue
            is_auth = True
            c.send_line('OK::login successfully')
            continue
        if cmd == 'ping':
            c.send_line('OK::pong')
            continue
        if cmd == 'exit' or cmd == 'bye':
            c.send_line('OK::bye')
            c.disconnect()
            break
        if is_auth == False:
            c.send_line('ERR::please auth first')
            continue
        if cmd == 'cd':
            if len(args) == 0:
                c.send_line('ERR::Invalid Parameters')
                continue
            try:
                os.chdir(args[0])
                c.send_line('OK::successfully chdir')
            except:
                c.send_line('ERR::Invalid Path')
            continue
        if cmd == 'ls' or cmd == 'dir':
            if os.name == 'nt':
                cmd = 'dir'
            elif os.name == 'posix':
                cmd = 'ls -al'
            else:
                c.send_line('ERR::%s command is not implemented in OS %s' % (cmd, os.name))
                continue
            if args == []: args = ['.']
            ret = os.popen('%s %s' % (cmd, args[0])).read()
            send_bytes(c, ret)
            continue
        if cmd == 'get':
            if len(args) == 0:
                c.send_line('ERR::Invalid Parameters')
                continue
            if os.path.isfile(args[0]):
                with open(args[0], 'rb') as f:
                    ret = f.read()
                send_bytes(c, ret)
            else:
                c.send_line('ERR::File not exists')
            continue
        if cmd == 'put':
            if len(args) < 2:
                c.send_line('ERR::Invalid Parameters')
                continue
            try:
                file_len = int(args[1])
                if file_len < 0:
                    raise Exception
            except:
                c.send_line('ERR::Invalid length')
                continue
            if (not os.path.isfile(args[0]) and not os.path.isdir(args[0])) or (os.path.isfile(args[0]) and len(args) > 2 and args[2] == 'force'):
                try:
                    recv = c.recvn(file_len)
                except socket.timeout:
                    c.send_line('ERR::operation put timeout')
                    continue
                with open(args[0], 'wb') as f:
                    f.write(recv)
                c.send_line('OK::Successfully written')
            else:
                c.send_line('ERR::There is a directory or a file in this path. If you want to overwrite the file, add parameter "force" after the command.')
            continue
        if cmd == 'shell' or cmd == 'sh' or cmd == 'bash':
            ret = os.popen(' '.join(args)).read()
            send_bytes(c, ret)
            continue
        c.send_line('ERR::Unknown command: ' + cmd)
            

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((sys.argv[1], int(sys.argv[2])))

while True:
    client_handler(s, raw_input())