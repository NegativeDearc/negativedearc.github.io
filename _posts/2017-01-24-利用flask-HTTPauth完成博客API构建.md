---
layout: page
title: 利用flask-HTTPauth完成博客API构建
tags: ['Python', 'Flask', 'Flask-HTTPauth']
categories: ['编程']
date: 2017-01-24 16:13:00
---
为了配合页面各种ajax的使用需求，设计自己博客的API需求日益增加。由于我采用flask作为我的web框架，自然想到使用flask-HTTPauth作为扩展，由flask作者亲自开发，质量自然有保证。

- github地址 https://github.com/miguelgrinberg/Flask-HTTPAuth
- 中文文档地址 http://www.pythondoc.com/flask-restful/third.html
- 英文文档地址 http://flask-httpauth.readthedocs.io/en/latest/

建议阅读英文文档，之前由于对HTTP协议一无所知，在带token认证这一步卡了很久。后来查到如下：

> The `verify_token` callback receives the authentication credentials provided by the client on the `Authorization` header. This can be a simple token, or can contain multiple arguments, which the function will have to parse and extract from the string

需要把客户端生成的token放入HTTP请求头部的Authorization字段中，在ajax中是这样的：

{% highlight javascript %}

$.ajax({
    beforeSend:function (request) {
      request.setRequestHeader("Authorization", BasicAuthorizationCode(token,"unused"));
    },
    type:'...',
    url:'...'
    data:{"_method":"DELETE"},
    dataType:"json",
    success:function () {
      ...
    }
});

{% endhighlight %}

请求里面带了unused字段，替代密码的占位符，可以被任意字符替代，以上则完成了一次BASIC认证。其中BasicAuthorizationCode是一个对token进行base64二进制转化的函数。

带token的认证方式，减少了用户名和密码传输的次数，但还是需要用户名密码获得token，在我的博客中我分配了一个URL专门用来处理请求token。必须是经过登陆的用户才能请求token，但如果我们想在js代码中请求到该URL势必要将用户名和密码明文写入代码之中。

由于我没有查到如何处理这种情况，我采取了一个折中的办法：

{% highlight python %}

@main.route('/test/token', methods=["GET", "POST"])
@login_required
def main_verify_token(expires=600):
    token = g.user.generate_auth_token(expiration=expires)
    return jsonify({"token": token})

{% endhighlight %}

使用flask-login的装饰器确保只有经过登陆的用户才能访问该路由。尽管功能上已经可以满足我的要求了，但在概念上仍然模糊。

1. 什么是无状态？
1. 如何实现无状态？
1. 如何设计一个合理的API？

学习之路漫漫，除了想象力还需要扎扎实实读源码的功力