---
layout: page
title: SQLALCHEMY超级灵活的事件监听使用方法
tags: ['Python', 'Sqlalchemy']
categories: ['编程']
date: 2017-02-08 17:12:00
---

SQLALCHEMY中ORM语句特别灵活，通常，我们使用来自session.query产生的Query对象进行增删改。

{% highlight python %}
q = session.query(SomeClass)
{% endhighlight %}

而在flask-sqlalchemy中，作者新增了一个BaseQuery类，使我们可以对一个有效模型类，进行查询，例如

{% highlight python lineanchors %}
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
	
    @classmethod
    def exist_susan(cls):
        rv = cls.query.filter(name= 'Susan').one()
        return True if rv else False
{% endhighlight %}

由于这种方法自动替我们处理好了session，省心快捷，在我的开发当中，大量使用了这种写法。然而在后期这种写法对模型进行事件监听的造成了很多困难。

#### 监听after_delete事件失败

{% highlight python %}
cls.query.filter(cls.id == row_id).delete()
{% endhighlight %}

#### 监听after_delete时间成功

{% highlight python %}
rv = cls.query.filter(cls.id == row_id).first()
db.session.delete(rv)
db.session.commit()
{% endhighlight %}

在此，我总结了一个常见事件对应的推荐写法供大家参考。

1.使用after_insert/before_insert事件
{% highlight python %}
user = User(name="susan",age=20)
db.session.add(user)
db.session.commit()
{% endhighlight %}

2.使用after_update/before_update事件

{% highlight python %}
\#以下写法无效
db.session.query(User).filter(User.name == "susan").update({"age": 18})
db.session.commit()
{% endhighlight %}

为什么会无效呢，是不是感觉很奇怪，查了API发现

> The [MapperEvents.before_delete()](!https://docs.sqlalchemy.org/en/latest/orm/events.html#sqlalchemy.orm.events.MapperEvents.before_delete)and [MapperEvents.after_delete()](https://docs.sqlalchemy.org/en/latest/orm/events.html#sqlalchemy.orm.events.MapperEvents.after_delete) events are not invoked from this method. Instead, the [SessionEvents.after_bulk_delete()](https://docs.sqlalchemy.org/en/latest/orm/events.html#sqlalchemy.orm.events.SessionEvents.after_bulk_delete) method is provided to act upon a mass DELETE of entity rows

所以你想用上面的写法，你得把事件改为after_bulk_delete事件。在flask-sqlalchemy已经替你完成了session的自动化产生和销毁，并且全局唯一，想要使用这个事件，还需要做很多额外的工作去处理session问题。但如果你只想针对某个字段使用update监听，我们还有另外的方法——即使用Attribute Event中的[set](https://docs.sqlalchemy.org/en/latest/orm/events.html#attribute-events)方法

{% highlight python %}
susan = db.session.query(User).filter(User.name == "susan")
susan.age = 18 # set 方法监听成功
db.session.commit()
{% endhighlight %}

这样也完成了一次update操作。