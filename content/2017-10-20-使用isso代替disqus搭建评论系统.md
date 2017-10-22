Title: 使用isso代替disqus搭建评论系统
Category: 编程
Tags: Python
Date: 2017-10-20 22:16:00
Modified: 2017-10-22 11:31:00


### 前言
一直想搭建一个self-hosted的评论系统，心里种草很久。多说的倒闭、Disqus在国内无法访问，加上技术储备并不充分，虽然尝试写了一个非常简单评论功能，见[文章](http://www.kukumalu.cc/li-yong-jinjahong-ji-sqlite-cteshe-ji-lei-si-wang-yi-ping-lun-de-hui-fu-xi-tong.html)，和预期相差甚远。

一方面在互联网搜索各式的开源评论系统设计，

- 说吧，基于Node.js和MongoDB&nbsp;[yuyouwen/shuoba](https://github.com/yuyouwen/shuoba)
- Gitment，基于Github Issue&nbsp;[imsun/gitment](https://github.com/imsun/gitment)
- Isso，基于python和SQLite，Disqus的替代品&nbsp;[posativ/isso](https://github.com/posativ/isso)

一方面也终于抽出时间尝试。这篇文章记录了基于Python的isso的搭建过程和一些“坑”及解决方案。


### 准备工作
Isso强烈建议评论系统不应直接暴露在公网环境，同时以作为sub URI作为评论访问地址，能够避免一些强隐私保护浏览器屏蔽评论。但会带来跨域资源共享问题([CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS))。


#### 二级域名解析
以本博客[kukumalu.cc](http://www.kukumalu.cc)为例, 申请了[comment.kukumalu.cc](comment.kukumalu.cc)作为二级域名，在阿里云设置了A纪录解析到服务器。

- 解析到自己网站，[说明](https://help.aliyun.com/knowledge_detail/39785.html)
- 解析到其他网站，[??]()


#### 配置准备

***isso.cfg***

```
[general]
# 数据库所在路径
dbpath = /var/lib/isso/comments.db

# 你的主机域名，注意不是评论系统所在域名, Isso会自动处理CORS
host = http://www.kukumalu.cc

# 允许用户移除、编辑评论的最大时间
max-age = 15m

# 获得评论相关通知的方式
# stdout
#     Log to standard output. Default, if none selected.
# smtp
#     Send notifications via SMTP on new comments with activation (if
#     moderated) and deletion links.
notify = stdout

# 日志文件存放路径
log-file = /var/log/isso/isso.log

#################################
#后面配置保持默认，可运行，按需修改#
#################################

[moderation]
# 评论审核相关配置
# Comments in modertion queue are not visible to other users until you activate
# them.
enabled = false

# remove unprocessed comments in moderation queue after given time.
purge-after = 30d


[server]
# 服务端相关配置
# interface to listen on. Isso supports TCP/IP and unix domain sockets: UNIX
# domain socket listen = unix:///tmp/isso.sock TCP/IP listen =
# http:///localhost:1234/
#
# When gevent is available, it is automatically used for http:// Currently,
# gevent can not handle http requests on unix domain socket (see #295 and #299
# for details).  Does not apply for uWSGI.
listen = http://localhost:8080

# reload application, when the source code has changed. Useful for development.
# Only works with the internal webserver.
reload = off

# show 10 most time consuming function in Isso after each request. Do not use
# in production.
profile = off


[smtp]
# 邮件通知相关配置
# Isso can notify you on new comments via SMTP. In the email notification, you
# also can moderate (=activate or delete) comments.

# self-explanatory, optional
username =

# self-explanatory (yes, plain text, create a dedicated account for
# notifications), optional.
password =

# SMTP server
host = localhost

# SMTP port
port = 587

# use a secure connection to the server, possible values: none, starttls or
# ssl. Note, that there is no easy way for Python 2.7 and 3.3 to implement
# certification validation and thus the connection is vulnerable to
# Man-in-the-Middle attacks. You should definitely use a dedicated SMTP account
# for Isso in that case.
security = starttls

# recipient address, e.g. your email address
to =

# sender address, e.g. "Foo Bar" <isso@example.tld>
from =

# specify a timeout in seconds for blocking operations like the
# connection attempt.
timeout = 10


[guard]
# 反垃圾机制
# Enable basic spam protection features, e.g. rate-limit per IP address (/24
# for IPv4, /48 for IPv6).

# enable guard, recommended in production. Not useful for debugging purposes.
enabled = true

# limit to N new comments per minute.
ratelimit = 2

# how many comments directly to the thread (prevent a simple while true; do
# curl ...; done.
direct-reply = 3

# allow commenters to reply to their own comments when they could still edit
# the comment. After the editing timeframe is gone, commenters can reply to
# their own comments anyways. Do not forget to configure the client.
reply-to-self = true

# force commenters to enter a value into the author field. No validation is
# performed on the provided value.  Do not forget to configure the client
# accordingly.
require-author = true

# require the commenter to enter an email address (note: no validation is
# done on the provided address). Do not forget to configure the client.
require-email = true


[markup]
# 评论内容机制
# Customize markup and sanitized HTML. Currently, only Markdown (via Misaka) is
# supported, but new languages are relatively easy to add.

# Misaka-specific Markdown extensions, all flags starting with EXT_ can be used
# there, separated by comma.
options = strikethrough, autolink, fenced_code, no_intra_emphasis

# Additional HTML tags to allow in the generated output, comma-separated. By
# default, only a, blockquote, br, code, del, em, h1, h2, h3, h4, h5, h6, hr,
# ins, li, ol, p, pre, strong, table, tbody, td, th, thead and ul are allowed.
allowed-elements =

# Additional HTML attributes (independent from elements) to allow in the
# generated output, comma-separated. By default, only align and href are
# allowed.
allowed-attributes =


[hash]
# 安全相关
# Customize used hash functions to hide the actual email addresses from
# commenters but still be able to generate an identicon.


# A salt is used to protect against rainbow tables. Isso does not make use of
# pepper (yet). The default value has been in use since the release of Isso and
# generates the same identicons for same addresses across installations.
salt = Eech7co8Ohloopo9Ol6baimi

# Hash algorithm to use -- either from Python's hashlib or PBKDF2 (a
# computational expensive hash function).
#
# The actual identifier for PBKDF2 is pbkdf2:1000:6:sha1, which means 1000
# iterations, 6 bytes to generate and SHA1 as pseudo-random family used for key
# strengthening. Arguments have to be in that order, but can be reduced to
# pbkdf2:4096 for example to override the iterations only.
```

#### 修改模板
配置完服务端，客户段(JS)需要相应修改，由于我使用的是Pelican静态博客生成工具，在主题文件夹新增了一个isso.html模板。

***isso.html***

```
:::html
{% if ISSO_RUNNING %}

<section id="isso-thread"></section>
<script data-isso="//comment.kukumalu.cc/"  
    data-isso-css="true"
    data-isso-lang="en"
    data-isso-reply-to-self="true"
    data-isso-require-author="true"
    data-isso-require-email="true"
    data-isso-max-comments-top="10"
    data-isso-max-comments-nested="5"
    data-isso-reveal-on-click="5"
    data-isso-avatar="true"
    data-isso-avatar-bg="#f0f0f0"
    data-isso-avatar-fg="#9abf88 #5698c4 #e279a3 #9163b6 ..."
    data-isso-vote="true"
    data-vote-levels="[-5,5,15]"
    src="//comment.kukumalu.cc/js/embed.min.js"></script>

{% endif %}
```

Isso 通常会自动检测 REST API, 但如果 JS 文件(Isso的JS实例)并不在默认位置则需要修改 `data-isso`属性来覆写，值得注意的是`src`中URI写法并未包含http头。

JS端配置成功后，可以在网页中看到整个评论的form，在[http://comment.kukumalu.cc/info](http://comment.kukumalu.cc/info)也能查到关于Isso的信息。

#### Nginx 配置
先提供一些CORS Nginx配置的参考内容

- [https://enable-cors.org/server_nginx.html](https://enable-cors.org/server_nginx.html)
- [https://michielkalkman.com/snippets/nginx-cors-open-configuration/](https://michielkalkman.com/snippets/nginx-cors-open-configuration/)
- [http://m.blog.csdn.net/oyzl68/article/details/18741057](http://m.blog.csdn.net/oyzl68/article/details/18741057)
- [https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [http://xiaorui.cc/2016/03/07/在nginx配置cors请求的headers头部信息/](http://xiaorui.cc/2016/03/07/在nginx配置cors请求的headers头部信息/)

CORS在Isso包文档中谈及的不多，但我仅使用文档中的模板配置没用办法成功运行(500错误，CORS头部丢失)。nohup.out的错误信息如下:

```
127.0.0.1 - - [2017-10-22 15:04:10] "OPTIONS /count HTTP/1.0" 500 161 0.000654
Traceback (most recent call last):
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/gevent/pywsgi.py", line 935, in handle_one_response
    self.run_application()
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/gevent/pywsgi.py", line 908, in run_application
    self.result = self.application(self.environ, self.start_response)
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/werkzeug/contrib/fixers.py", line 152, in __call__
    return self.app(environ, start_response)
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/isso/wsgi.py", line 119, in __call__
    return self.app(environ, start_response)
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/isso/wsgi.py", line 147, in __call__
    add_cors_headers("200 Ok", [("Content-Type", "text/plain")])
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/isso/wsgi.py", line 144, in add_cors_headers
    return start_response(status, headers.to_list(), exc_info)
  File "/home/app/negativedearc.github.io/venv/local/lib/python2.7/site-packages/gevent/pywsgi.py", line 830, in start_response
    raise UnicodeError("The status string must be a native string")
UnicodeError: The status string must be a native string
Sun Oct 22 15:04:10 2017 {'REMOTE_PORT': '52242', 'HTTP_HOST': 'comment.kukumalu.cc', 'REMOTE_ADDR': '114.216.124.225', (hidden keys: 30)} failed with UnicodeError
```

Isso在其[wsgi.py](https://github.com/posativ/isso/blob/master/isso/wsgi.py#L122)中已经提前处理了CORS需要的头部信息。

```
:::python

class CORSMiddleware(object):
    """Add Cross-origin resource sharing headers to every request."""

    methods = ("HEAD", "GET", "POST", "PUT", "DELETE")

    def __init__(self, app, origin, allowed=None, exposed=None):
        self.app = app
        self.origin = origin
        self.allowed = allowed
        self.exposed = exposed

    def __call__(self, environ, start_response):

        def add_cors_headers(status, headers, exc_info=None):
            headers = Headers(headers)
            headers.add("Access-Control-Allow-Origin", self.origin(environ))
            headers.add("Access-Control-Allow-Credentials", "true")
            headers.add("Access-Control-Allow-Methods", ", ".join(self.methods))
            if self.allowed:
                headers.add("Access-Control-Allow-Headers", ", ".join(self.allowed))
            if self.exposed:
                headers.add("Access-Control-Expose-Headers", ", ".join(self.exposed))
            return start_response(status, headers.to_list(), exc_info)

        if environ.get("REQUEST_METHOD") == "OPTIONS":
            add_cors_headers("200 Ok", [("Content-Type", "text/plain")])
            return []

        return self.app(environ, add_cors_headers)
```
但似乎OPTIONS没有处理成功？推测原因：

- Nginx 没有(无法)正确处理OPTIONS请求，[参考资料](https://stackoverflow.com/questions/14929347/how-to-handle-options-request-in-nginx)
- wsgi MiddleWare 没有正确假如头部信息（需要确认，[参考资料](https://github.com/posativ/isso/issues/347)）。

无论如何，在改动Nginx配置（手动加入OPTIONS判断）后运行成功了。

***isso.conf***

```
:::nginx

server {
    listen         80;
    server_name    comment.kukumalu.cc;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;


        if ($request_method = 'OPTIONS') {
	        add_header 'Access-Control-Allow-Origin' 'http://www.kukumalu.cc';
	        add_header 'Access-Control-Allow-Methods' 'HEAD, GET, POST, PUT, DELETE';
	        add_header 'Access-Control-Allow-Credentials' 'true';
	        add_header 'Access-Control-Allow-Headers' 'Origin, Referer, Content-Type';

	        # Tell client that this pre-flight info is valid for 20 days
	   
	        add_header 'Access-Control-Max-Age' 1728000;
	        add_header 'Content-Type' 'text/plain; charset=utf-8';
	        add_header 'Content-Length' 0;
	        return 204;
        }
    }
```
放入vhost中与其它Nginx服务一起运行。

#### 运行
生产环境下，运行isso最简单的方式是使用`gevent`，两个步骤就可以搞定。

```
:::bash

pip install gevent -i https://pypi.douban.com/simple
isso -c isso.cfg run
```

至此，isso可以完美的运行起来。

### 其他
- 评论后台管理，目前pip版本暂无此功能提供，只能手动操作评论数据库，但全能的网友PR了作者(https://github.com/posativ/isso/pull/256)，由于作者非常忙，还没有Merge。
- 感谢[https://www.pupboss.com/build-a-comment-system-using-isso/](https://www.pupboss.com/build-a-comment-system-using-isso/)，可能是互联网找得到唯一一篇部署isso的博客。 
- github issue非常有用，项目的知识库对整个project的leverage具有非常大的推进、参考、风险避免的作用。