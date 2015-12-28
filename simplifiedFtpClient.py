import socket, thread, sys, connection, os, os.path

if len(sys.argv) <= 4:
    print 'Usage: python simplifiedFtpClient.py <host> <port> <username> <password>'
    exit()
    
is_verbose_mode = False
    
def parse_cmd(cmd_string):
    STH_STRANGE = '!@#$%^&*&^%$#@'
    cmd_array = cmd_string.replace('::::', STH_STRANGE).split('::')
    cmd_array = [x.replace(STH_STRANGE, '::') for x in cmd_array]
    return (cmd_array[0], cmd_array[1:])

def send_bytes(c, bytes):
    c.send_line('OK::sending::%d' % len(bytes))
    c.send(bytes)
    
def confirm(msg):
    print msg + ' (y/n)'
    r = raw_input()
    while not (r in ['y','Y','n','N']):
        print msg + '(y/n)'
        r = raw_input()
    return (r in ['y', 'Y'])
    
def parse_bytes_stream_mode(header, c):
    global is_verbose_mode
    ret, ret_args = parse_cmd(header)
    if ret == 'ERR':
        print 'ERR::' + '::'.join(ret_args)
        return
    if ret == 'OK' and len(ret_args) == 2 and ret_args[1] == 'sending':
        try:
            file_len = int(ret_args[1])
            if file_len < 0: raise Exception
        except:
            print 'ERR::Invalid response - Len: ' + ret_args[1]
            return
    else:
        print 'ERR::Invalid response - ' + recv
        return
    body = c.recvn(file_len)
    if is_verbose_mode: print '> (%d bytes received)' % file_len
    return body
        
def client_handler(c):
    global is_verbose_mode

    raw_prompt = c.recv_until('$ ')
    if is_verbose_mode: print '> ' + raw_prompt
    remote_path = raw_prompt[raw_prompt.find('@')+1:-2]
    sys.stdout.write('sFTP@%s:%s::%s:%s$ ' % (sys.argv[1], sys.argv[2], os.getcwd(), remote_path))
    raw_string = raw_input()
    cmd, args = parse_cmd(raw_string)
    
    if cmd == 'exit' or cmd == 'bye':
        c.send_line('exit')
        c.disconnect()
        exit()
        
    if cmd == 'verbose':
        is_verbose_mode = not is_verbose_mode
        print ('verbose mode enabled' if is_verbose_mode else 'verbose mode disabled')
        return
        
    if cmd == 'downloadto':
        if len(args) < 2:
            print 'ERR::Invalid Parameters'
            return
        if os.path.isfile(args[1]):
            if not confirm(args[1] + ' exists, overwrite?'):
                return
        if os.path.isdir(args[1]):
            print 'ERR::There is a directory at ' + args[1]
            return
        c.send_line('get::' + args[0])
        if is_verbose_mode: print '< get::' + args[0]
        recv = c.recv_until('\n')
        if is_verbose_mode: print '> ' + recv
        body = parse_bytes_stream_mode(recv, c)
        if not (body is None):
            with open(args[1], 'wb') as f:
                f.write(body)
        print 'OK::%d bytes written to %s' % (len(body), args[1])
        return True
        
    if cmd == 'uploadto':
        if len(args) < 2:
            print 'ERR::Invalid Parameters'
            return
        if not os.path.isfile(args[0]):
            print 'ERR::cannot open local file ' + args[0]
            return
        with open(args[0], 'rb') as f:
            body = f.read()
        sftp_cmd = 'put::%s::%d' % (args[1], len(body))
        if len(args) >= 3 and args[2] == 'force':
            sftp_cmd += '::force'
        c.send_line(sftp_cmd)
        if is_verbose_mode: print '< ' + sftc_cmd
        recv = c.recv_until('\n')
        if is_verbose_mode: print '> ' + recv
        ret, ret_args = parse_cmd(recv)
        if ret == 'OK':
            if len(ret_args) >= 2 and ret_args[0] == 'waiting':
                c.send(body)
                if is_verbose_mode: print '< (%d bytes sent)' % len(body)
                recv = c.recv_until('\n')
                if is_verbose_mode: print '> ' + recv
                print recv
                return True
            else:
                print 'ERR::Unknown response. Exiting...'
                c.disconnect()
                exit()
        else:
            print '::'.join([ret]+ret_args)
            return True
            
    if cmd in ['lsh', 'localshell', 'lcmd']:
        ret = os.popen(' '.join(args)).read()
        print ret
        return
        
    if cmd == 'lcd' or cmd == 'localcd':
        if len(args) == 0:
            print 'ERR::Invalid Parameters'
            return
        try:
            os.chdir(args[0])
            print 'OK::successfully chdir'
        except:
            print 'ERR::Invalid Path'
        return
        
    if cmd == 'lls' or cmd == 'ldir':
        if os.name == 'nt':
            cmd = 'dir'
        elif os.name == 'posix':
            cmd = 'ls -al'
        else:
            print 'ERR::%s command is not implemented in OS %s' % (cmd, os.name)
            return
        if args == []: args = ['.']
        print os.popen('%s %s' % (cmd, args[0])).read()
        return

    c.send_line(raw_string)
    if is_verbose_mode: print '< ' + raw_string
    recv = c.recv_until('\n')
    if is_verbose_mode: print '> ' + recv
    ret, ret_args = parse_cmd(recv)
    if len(ret_args) > 0:
        if ret == 'OK' and (ret_args[0] == 'waiting' or ret_args[0] == 'sending'):
            try:
                body_len = int(ret_args[1])
                if body_len < 0: raise Exception
            except:
                print recv
                print 'ERR: invalid length - ' + ret_args[1]
                print 'Exiting...'
                exit()
            if ret_args[0] == 'sending':
                body = c.recvn(body_len)
                print '> (%d bytes received)' % body_len
                print body
                return True
            else:
                print recv
                buf = ''
                while len(buf) < body_len:
                    buf += raw_input() + '\n'
                c.send(buf[:body_len])
                return True
    print recv
    return True

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((sys.argv[1], int(sys.argv[2])))
c = connection.Connection(s)
welcome_msg = c.recv_until('\n')
if welcome_msg.find('Welcome to Simplified FTP Server V') == -1:
    print 'Not a valid Simplified FTP Server.'
    exit()
c.recv_until('$ ')
c.send_line('auth::%s::%s' % (sys.argv[3], sys.argv[4]))
if c.recv_until('\n').split('::')[0] != 'OK':
    print 'Invalid username/password'
    exit()
    
print welcome_msg

while True:
    if not client_handler(c): c.send_line('ping')
    