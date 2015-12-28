# Simplified FTP协议及其服务器、客户端文档
网络课期末Project by Garzon

## 简介
Simplified FTP是一个工作在应用层的，基于TCP连接的实验性的文件传输协议。在这个project中，定义了Simplified FTP的内容，实现了Simplified FTP服务器及一个基于Simplified FTP协议扩展而来的命令行客户端。

## 代码
主要部分共分为simplifiedFtpServer.py和simplifiedFtpClient.py，即分别是服务端和客户端脚本(python2)。      
其中还有connection.py中Connection类是自己写的一个辅助socket操作的帮助类。        
另，simplifiedFtpClient.py只是一个*辅助性*的客户端，直接利用nc程序连接服务端也是可以的。       

## 部署

要运行服务端，请输入：
```bash
~$ python ./simplifiedFtpServer.py <监听端口号> <服务器username> <password>
```

要运行客户端，请输入：
```bash
~$ python ./simplifiedFtpClient.py <服务器ip> <端口号> <服务器username> <password>
```

## Simplified FTP协议spec
client端建立socket连接后，server端会新开一个线程处理连接，并会返回欢迎信息如下：
```
Welcome to Simplified FTP Server V<版本号>!
$ 
```
此时可以输入Simplified FTP命令，命令列表如下所示。但首先需输入auth命令登录，否则大多数命令无效。

### 命令
命令的语法为：`命令::参数1::参数2...`，即分隔符为`::`而不是空格，如在参数中包含有`::`的特殊情况，需要转义的话，用`::::`代替。    
输入命令后，服务端会返回信息，格式如下：
```
OK::<提示信息>
或
ERR::<错误信息>
```

注意后面会跟着一个`\n`字符

#### 字节流模式
其中，形如：
```
OK::sending::<字节长度>
```
的返回信息表示服务器还将会紧接着返回<字节长度>长的字节流，称为字节流模式。字节流模式结束后不会返回换行符。     

#### 输出完毕后
服务器会返回命令提示符
```
simplifiedFTP@<当前服务器端工作目录>$ 
```

注意开头不含换行符，结尾含有一个空格，不含换行符。

### Simplified FTP命令一览表
涉及server端的操作统称为远程命令，命令列表如下：

#### auth::<登录用户名>::<密码>
表示用此登录凭据登录服务器，以便进行下一步操作。
成功登陆返回`OK::login successfully`，登录凭据无效返回`ERR::Invalid username/password`

#### ping
发送心跳信息，用于维持连接或检测连接状态，正常应返回`OK::pong`

#### exit 或 bye
表示断开连接，正常返回`OK::bye`

#### cd::<目录>
表示切换服务端工作目录至<目录>，成功返回`OK::successfully chdir`，失败返回`ERR::Invalid Path`

#### ls 或 dir::[目录 = ./]
表示列出该<目录>文件，默认为`./`，成功为返回字节流模式

#### get::<服务端文件路径>
表示获取该<文件>内容，成功返回字节流模式，错误返回`ERR::File not exists`

#### put::<服务端文件存放路径>::<字节长度>::[force]
输入该命令后，若服务器返回`OK::waiting::<字节长度>`，应紧接着发送<字节长度>长的字节流，表示服务器应把字节流保存在<文件路径>中，     
字节长度应为非负数，否则返回`ERR::Invalid length`，     
如果路径已存在目录或文件，返回`ERR::There is a directory or a file in this path. If you want to overwrite the file, add parameter "force" after the command.`     
若强制覆盖文件，请加入`force`参数，但不会覆盖文件夹     
超时返回`ERR::operation put timeout`      
成功返回`OK::Successfully written`

#### shell或sh或bash或cmd::<命令字符串>::[<命令参数1>::<命令参数2>::....]
表示在服务器上执行命令，返回命令输出，字符流模式。

### 服务端错误返回信息一览表

```
ERR::Invalid Parameters
```
表示参数数目不对

```
ERR::Unknown command: <输入的命令>
```
表示无效的命令

```
ERR::please auth first
```
表示需要登录才能进一步操作

## Simplified FTP客户端说明
Simplified FTP客户端是一个基于Simplified FTP协议之上的辅助性客户端，增加了一些便于命令行操作的仿Simplified FTP样式的命令。

### 客户端命令提示符
命令提示符形式如下：
```
sFTP@<服务器ip>::<本地工作路径>:<远程工作路径>$ 
```

### 客户端命令一览

#### Simplified FTP协议原生命令
除了客户端特有的命令，其他命令将直接被发送至服务端处理，所以客户端是支持所有Simplified FTP协议原生命令的。

#### downloadto::<远程文件地址>::<本地保存路径>
客户端对原生命令`get`的封装，将获取的<远程文件>保存至<本地路径>

#### uploadto::<本地文件地址>::<远程保存路径>
客户端对原生命令`put`的封装，将<本地文件>保存至服务器<远程路径>

#### localshell或lsh或lcmd::<命令字符串>::[<命令参数1>::<命令参数2>::....]
在本地执行<命令>

#### localcd或lcd::<目录>
表示切换本地工作目录至<目录>

#### lls或ldir::[目录 = ./]
列出<本地目录>的文件

#### verbose
显示/隐藏调试信息，调试信息即是服务器与客户端的原始通信过程，`>`表示接收到来自服务器的信息，`<`表示发送至服务器。

## 实验

### 实验1: 直接连接服务器
这是直接利用linux下的nc程序连接服务器的实验，实验结果如下：

```
garzon@garzons-lib:~$ nc localhost 8895
Welcome to Simplified FTP Server V1.0!
$ auth::wrong::usernameandpassword
ERR::Invalid username/password
$ auth::username::password
OK::login successfully
simplifiedFTP@/home/garzon/test2$ ls
OK::sending::320
总用量 36
drwxrwxr-x   2 garzon garzon  4096 12月 28 18:36 .
drwxr-xr-x 126 garzon garzon 12288 12月 28 17:00 ..
-rw-r--r--   1 garzon garzon  3999 12月 28 17:14 connection.py
-rw-r--r--   1 garzon garzon  4623 12月 28 18:36 connection.pyc
-rw-r--r--   1 garzon garzon  4582 12月 28 17:57 simplifiedFtpServer.py
simplifiedFTP@/home/garzon/test2$ dir
OK::sending::320
总用量 36
drwxrwxr-x   2 garzon garzon  4096 12月 28 18:36 .
drwxr-xr-x 126 garzon garzon 12288 12月 28 17:00 ..
-rw-r--r--   1 garzon garzon  3999 12月 28 17:14 connection.py
-rw-r--r--   1 garzon garzon  4623 12月 28 18:36 connection.pyc
-rw-r--r--   1 garzon garzon  4582 12月 28 17:57 simplifiedFtpServer.py
simplifiedFTP@/home/garzon/test2$ put::1.test::10
OK::waiting::10
helloworld
OK::Successfully written
simplifiedFTP@/home/garzon/test2$ ls
OK::sending::377
总用量 40
drwxrwxr-x   2 garzon garzon  4096 12月 28 18:38 .
drwxr-xr-x 126 garzon garzon 12288 12月 28 17:00 ..
-rw-rw-r--   1 garzon garzon    10 12月 28 18:38 1.test
-rw-r--r--   1 garzon garzon  3999 12月 28 17:14 connection.py
-rw-r--r--   1 garzon garzon  4623 12月 28 18:36 connection.pyc
-rw-r--r--   1 garzon garzon  4582 12月 28 17:57 simplifiedFtpServer.py
simplifiedFTP@/home/garzon/test2$ get::1.test
OK::sending::10
helloworldsimplifiedFTP@/home/garzon/test2$ get::not.exists
ERR::File not exists
simplifiedFTP@/home/garzon/test2$ put::1.test::1
ERR::There is a directory or a file in this path. If you want to overwrite the file, add parameter "force" after the command.
simplifiedFTP@/home/garzon/test2$ ls
OK::sending::377
总用量 40
drwxrwxr-x   2 garzon garzon  4096 12月 28 18:38 .
drwxr-xr-x 126 garzon garzon 12288 12月 28 17:00 ..
-rw-rw-r--   1 garzon garzon    10 12月 28 18:38 1.test
-rw-r--r--   1 garzon garzon  3999 12月 28 17:14 connection.py
-rw-r--r--   1 garzon garzon  4623 12月 28 18:36 connection.pyc
-rw-r--r--   1 garzon garzon  4582 12月 28 17:57 simplifiedFtpServer.py
simplifiedFTP@/home/garzon/test2$ sh::rm::1.test
OK::sending::0
simplifiedFTP@/home/garzon/test2$ ls
OK::sending::320
总用量 36
drwxrwxr-x   2 garzon garzon  4096 12月 28 18:38 .
drwxr-xr-x 126 garzon garzon 12288 12月 28 17:00 ..
-rw-r--r--   1 garzon garzon  3999 12月 28 17:14 connection.py
-rw-r--r--   1 garzon garzon  4623 12月 28 18:36 connection.pyc
-rw-r--r--   1 garzon garzon  4582 12月 28 17:57 simplifiedFtpServer.py
simplifiedFTP@/home/garzon/test2$ bye
OK::bye
```

### 实验2：利用客户端连接服务器

```
garzon@garzons-lib:~/test2$ python simplifiedFtpClient.py 
Usage: python simplifiedFtpClient.py <host> <port> <username> <password>
garzon@garzons-lib:~/test2$ python simplifiedFtpClient.py localhost 8895 username password
Welcome to Simplified FTP Server V1.0!

sFTP@localhost:8895::/home/garzon/test2:/home/garzon/test2$ lcd ../test3
ERR::Unknown command: lcd ../test3

sFTP@localhost:8895::/home/garzon/test2:/home/garzon/test2$ lcd::../tets^H^H
ERR::Invalid Path
sFTP@localhost:8895::/home/garzon/test2:/home/garzon/test2$ lcd::../test3
OK::successfully chdir
sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ cat abc.txt
ERR::Unknown command: cat abc.txt

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ lsh::cat::abc.txt
abc

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ ls
> (516 bytes received)
总用量 52
drwxrwxr-x   2 garzon garzon  4096 12月 28 20:21 .
drwxr-xr-x 127 garzon garzon 12288 12月 28 20:15 ..
-rw-r--r--   1 garzon garzon  4070 12月 28 20:12 connection.py
-rw-r--r--   1 garzon garzon  4631 12月 28 20:12 connection.pyc
-rw-rw-r--   1 garzon garzon     1 12月 28 20:16 remote2.txt
-rw-rw-r--   1 garzon garzon     1 12月 28 20:16 remote.txt
-rw-r--r--   1 garzon garzon  6570 12月 28 20:21 simplifiedFtpClient.py
-rw-r--r--   1 garzon garzon  4673 12月 28 19:56 simplifiedFtpServer.py

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ uploadto::abc.txt::remoteabc.txt
OK::Successfully written

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ bash::cat::remoteabc.txt
> (4 bytes received)
abc

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ lsh::echo::"def"::>::def.txt

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ lls
总用量 24
drwxrwxr-x   2 garzon garzon  4096 12月 28 20:24 .
drwxr-xr-x 127 garzon garzon 12288 12月 28 20:15 ..
-rw-rw-r--   1 garzon garzon     4 12月 28 20:22 abc.txt
-rw-rw-r--   1 garzon garzon     4 12月 28 20:24 def.txt

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ lsh::cat::def.txt
def

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ uploadto::def.txt::remoteabc.txt
ERR::There is a directory or a file in this path. If you want to overwrite the file, add parameter "force" after the command.

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ uploadto::def.txt::remoteabc.txt::force
OK::Successfully written

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ bash::cat::remoteabc.txt
> (4 bytes received)
def

sFTP@localhost:8895::/home/garzon/test3:/home/garzon/test2$ bye
```

### 实验3：windows客户端与linux服务器交互

```
D:\simplifiedFTP>python simplifiedFtpClient.py 10.141.246.114 8895 username password
Welcome to Simplified FTP Server V1.0!

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ lls
 驱动器 D 中的卷是 Data
 卷的序列号是 2AAB-319D

 D:\simplifiedFTP 的目录

2015/12/28  20:33    <DIR>          .
2015/12/28  20:33    <DIR>          ..
2015/12/28  15:43                11 .gitignore
2015/12/28  20:12             4,070 connection.py
2015/12/28  20:33             4,601 connection.pyc
2015/12/28  20:27            11,098 README.md
2015/12/28  20:37             6,576 simplifiedFtpClient.py
2015/12/28  19:56             4,673 simplifiedFtpServer.py
               6 个文件         31,029 字节
               2 个目录 15,987,085,312 可用字节

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ ls
> (580 bytes received)
鎬荤敤閲?56
drwxrwxr-x   2 garzon garzon  4096 12鏈?28 20:23 .
drwxr-xr-x 127 garzon garzon 12288 12鏈?28 20:15 ..
-rw-r--r--   1 garzon garzon  4070 12鏈?28 20:12 connection.py
-rw-r--r--   1 garzon garzon  4631 12鏈?28 20:12 connection.pyc
-rw-rw-r--   1 garzon garzon    10 12鏈?28 20:26 remote2.txt
-rw-rw-r--   1 garzon garzon     4 12鏈?28 20:25 remoteabc.txt
-rw-rw-r--   1 garzon garzon     1 12鏈?28 20:16 remote.txt
-rw-r--r--   1 garzon garzon  6570 12鏈?28 20:21 simplifiedFtpClient.py
-rw-r--r--   1 garzon garzon  4673 12鏈?28 19:56 simplifiedFtpServer.py

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ downloadto::remoteabc.txt::windowsabc.txt
OK::4 bytes written to windowsabc.txt
sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ lls
 驱动器 D 中的卷是 Data
 卷的序列号是 2AAB-319D

 D:\simplifiedFTP 的目录

2015/12/28  20:37    <DIR>          .
2015/12/28  20:37    <DIR>          ..
2015/12/28  15:43                11 .gitignore
2015/12/28  20:12             4,070 connection.py
2015/12/28  20:33             4,601 connection.pyc
2015/12/28  20:27            11,098 README.md
2015/12/28  20:37             6,576 simplifiedFtpClient.py
2015/12/28  19:56             4,673 simplifiedFtpServer.py
2015/12/28  20:37                 4 windowsabc.txt
               7 个文件         31,033 字节
               2 个目录 15,987,085,312 可用字节

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ downloadto::remote.txt::windowsabc.txt
windowsabc.txt exists, overwrite? (y/n)
sdgs
windowsabc.txt exists, overwrite?(y/n)
y
OK::1 bytes written to windowsabc.txt
sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ lls
 驱动器 D 中的卷是 Data
 卷的序列号是 2AAB-319D

 D:\simplifiedFTP 的目录

2015/12/28  20:37    <DIR>          .
2015/12/28  20:37    <DIR>          ..
2015/12/28  15:43                11 .gitignore
2015/12/28  20:12             4,070 connection.py
2015/12/28  20:33             4,601 connection.pyc
2015/12/28  20:27            11,098 README.md
2015/12/28  20:37             6,576 simplifiedFtpClient.py
2015/12/28  19:56             4,673 simplifiedFtpServer.py
2015/12/28  20:38                 1 windowsabc.txt
               7 个文件         31,030 字节
               2 个目录 15,987,085,312 可用字节

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ uploadto::windowsabc.txt::fromwindows.txt
OK::Successfully written

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ ls
> (646 bytes received)
鎬荤敤閲?60
drwxrwxr-x   2 garzon garzon  4096 12鏈?28 20:38 .
drwxr-xr-x 127 garzon garzon 12288 12鏈?28 20:15 ..
-rw-r--r--   1 garzon garzon  4070 12鏈?28 20:12 connection.py
-rw-r--r--   1 garzon garzon  4631 12鏈?28 20:12 connection.pyc
-rw-rw-r--   1 garzon garzon     1 12鏈?28 20:38 fromwindows.txt
-rw-rw-r--   1 garzon garzon    10 12鏈?28 20:26 remote2.txt
-rw-rw-r--   1 garzon garzon     4 12鏈?28 20:25 remoteabc.txt
-rw-rw-r--   1 garzon garzon     1 12鏈?28 20:16 remote.txt
-rw-r--r--   1 garzon garzon  6570 12鏈?28 20:21 simplifiedFtpClient.py
-rw-r--r--   1 garzon garzon  4673 12鏈?28 19:56 simplifiedFtpServer.py

sFTP@10.141.246.114:8895::D:\simplifiedFTP:/home/garzon/test2$ exit
```