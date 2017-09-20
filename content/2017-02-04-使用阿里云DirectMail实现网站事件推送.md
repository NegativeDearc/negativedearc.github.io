---
layout: page
title: 使用阿里云DirectMail实现网站事件推送
tags: ['Python', 'DirectMail']
categories: ['编程']
date: 2017-02-04 11:06:00
---
接上期文章，监听数据库事件之后，我们有了特定情形下通知的诉求，通常来说e-mail比较经济方便。起初在163注册了一个邮箱，结果发现什么admin@cxwloves.cc啊，web_admin@cxwloves.cc之类基本大家都能想到的账号全都被注册干净了，让人不得不怀疑背后是否存在一条产业链。

无奈选了一个比较冷门的地址注册，在邮箱设置里面打开SMTP/POP3服务，同时开启了第三方客户端登陆码。这样Python就能连接上了。兴冲冲的准备发出一份Hello World邮件，结果提示邮件被Rejected，原因是被认定为垃圾邮件。

百度了下发现个人注册的邮箱似乎以这种方式送达率很低，所以权衡之下找到了阿里云DirectMail做推送，每天200封的免费邮件已经足够。更让人惊喜的是邮箱地址绑定到了域名，这样浑然一体没有遗憾了。

**使用SMTP方式**

阿里云处于安全考虑，关闭了25端口。

**使用Web API方式**

参照了阿里的文档，试了几次才成功，文档写的确实有一点问题。我这里总结起来供参考。API方式参数有两类，一类是公共方法参数，比如发信的方式，发信的AccessKey，签名加密的方式，时间戳等；第二类是私有方法参数，主要和发信相关，如收件人，主题，邮件正文，邮件html等。

1. 准备好所有的参数，包括公共的和私有的，签名因为尚未计算不包含进去，对其进行A-Z升序排列
2. 按照上面的排序，以键值对&key=value的形式连接所有参数，然后进行URL编码，得到parameter_string
3. 根据你的请求方式（GET或者POST），如GET方式，则GET&/& + parameter_string，对这个拼接后结果再次进行URL编码得到sign_string
4. 计算sign_string的HMAC_SHA1得到signature
5. 把这个signature以键值对的&Signature=signature形式加入parameter_string最后，对整个paramter_string进行URL编码后请求

整个请求过程涉及了相当数量的库，有urllib，urllib2，hashlib，base64，hmac等。这儿以Python 2.7 为例简单介绍步骤中一些关键的算法。

HMAC_SHA1：

{% highlight python linenos %}

def HMAC_SHA1(key, string_to_sign=None):
    # generate HMAC_SHA1 token
    signature = base64.b64encode(
        hmac.new(key, string_to_sign, hashlib.sha1).digest()
    )
    return signature

{% endhighlight %}

当地时间向UTC时间的转换：

{% highlight python linenos %}

def local_to_utc():
    # turn local time to UTC
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    return datetime.utcnow().strftime(format=UTC_FORMAT)

{% endhighlight %}

URL编码注意点：

- 空格需要编码，使用urllib.quote_plus()会导致空格转换成+而非%20，应该使用urllib.quote()
- "/"也需要进行编码，它的结果应该是%2F，应该使用`urllib.quote(string, safe="")`

这两点如果没有满足，签名计算就会出错，通不过服务器的验证邮件是没有办法被发送的。