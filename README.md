# Simplified FTP协议文档
网络课期末project

## 代码
主要部分共分为simplifiedFtpServer.py和simplifiedFtpClient.py，即分别是服务端和客户端脚本。
其中还有connection.py是自己写的一些辅助函数。
另，simplifiedFtpClient.py只是一个*辅助性*的客户端，直接利用nc程序连接服务端也是可以的。

## 部署

要运行服务端，请输入：
```bash
~$ python ./simplifiedFtpServer.py <监听端口号>
```

要运行客户端，请输入：
```bash
~$ python ./simplifiedFtpClient.py <服务器ip> <端口号>
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
输入该命令后，应紧接着发送<字节长度>长的字节流，表示服务器应把字节流保存在<文件路径>中，     
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



## 实验

### 实验1: 直接连接服务器
这是直接利用linux下的nc程序连接服务器的实验，如下：
```bash



```


