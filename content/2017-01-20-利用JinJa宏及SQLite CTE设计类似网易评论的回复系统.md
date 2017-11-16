title: 利用JinJa宏及SQLite CTE设计类似网易评论的回复系统
tags: Python, Flask, Jinja, SQLite
category: 编程
date: 2017-01-20 10:05:00
Modified: 2017-11-16 10:16:10 


本人从事和流程优化的工作，和计算机本无多大关系。后来阴差阳错渐渐自学编程，倒也找到了很多乐趣，当然也有很多坑。

这篇文章将作为记录我开发博客系统遇到的大大小小的坑中的首篇——也是卡住我最多时间思考的地方。

**如何制作一个类似网易盖楼的评论系统？**

问题就分解成了：

1. 如何设计数据库的评论表
2. 如何在视图中展示出嵌套的样式

在网上查了一些资料，

- 评论表有的是回复和评论功用一张表，但是必须要指定每一条评论的id以及它的回复对象pid，若是第一条回复，它的回复对象则是null。
- 也有方案是以回复和评论以两张表分开的形式存储

从降低耦合的角度出发，第二种方案更好，在第一种方案中假如需要删除评论，也许就会其他评论造成断档的问题。由于水平有限，我还是采取了第一种方案，理由是建表简单。

但是考虑到上述问题，我也设计了一个评论必须经过审核的逻辑，没有经过审核的评论是无法展示的，也就避免了展示后被删除的可能。

```
:::sql

CREATE TABLE "Comment" (
	id INTEGER NOT NULL, 
	uid VARCHAR(50) NOT NULL, 
	rdr_name VARCHAR(20) NOT NULL, 
	rdr_mail VARCHAR(20) NOT NULL, 
	rdr_message VARCHAR(200) NOT NULL, 
	reply_id VARCHAR(50) NOT NULL, 
	reply_to_id VARCHAR(50), 
	message_date DATETIME NOT NULL, 
	approved BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id), 
	UNIQUE (reply_id), 
	CHECK (approved IN (0, 1))
);
```

其中uid指向文章编号，reply_id会在每一次插入自动生成，reply_to_id就是它回复的评论的id。

有了这样的数据库，接下来就是要考虑如何提取数据的问题了。在一个文章地下，会有数十条评论，每一条评论下面还有层层嵌套的评论。查询的开销非常大，幸运的是，这样的递归查询，已经有了解决方案了——就是使用CTE（Common Table Expression），在我所用的sqlite3中版本号需要 >3.8.3。

首先遍历出所有评论，对每一条评论递归查询出它所有的回复。

```
:::sql

with recursive
     cte(id, reply_id, reply_to_id, rdr_message, rdr_name, message_date) as (
     select id, reply_id, reply_to_id, rdr_message, rdr_name ,message_date from Comment where reply_id = 'fa102480-dd21-11e6-b1ae-f4066974556c' and approved = 1 and uid = '3928f38e-d702-11e6-94'
     union all
     select Comment.id, Comment.reply_id, Comment.reply_to_id, Comment.rdr_message, Comment.rdr_name, Comment.message_date from Comment join cte on Comment.reply_id = cte.reply_to_id
     )
select * from cte
```

这样就获得了一个自下而上的的评论列表。这样结构的数据很难直接看出相互的继承关系，所以需要进一步处理使其结构嵌套起来，在python后端完成。

```
:::python

def nest(lst):
    """
    aim to turn flatten list (which fetched from sql) to nested structure
    :param lst: list
    :return: nested list
    """
    if not lst:
        return None
    first = lst[0]
    del lst[0]
    return {"pid": first, "id": nest(lst)}
```

这个递归函数会形成一个嵌套的字典表示层级关系提供给jinja模板进行递归渲染。

```
{% macro render_comment(comment, show_btn=True) %}
    <li class="comment">
        {{ media(comment["pid"], btn=show_btn) }}
        {% if comment["id"] %}
            <ul class="comment-ul">{{ render_comment(comment["id"], False) }}</ul>
        {% endif %}
    </li>
{% endmacro %}
```

其中的media也是一个宏，在我的界面里面我利用了bootstrap的media列表来展示评论，具体细节就不展示了，可以替换为任意的样式。

```
{% macro media(element, btn=True) %}
    <div class="media">
        <!--anchor-->
        <a name="comment-{{ element[0] }}" id="comment-{{ element[0] }}" style="display: none;"></a>
        <a href="#" class="pull-left"><img src="{{ element[3]|gravatar_url }}" alt="" class="media-object" width="25" height="25"></a>
        <div class="media-body">
            <div class="media-heading">{{ element[5] }} at {{ element[-1][:16] }}</div>
            <div class="media-content">{{ element[4] }}</div>
        </div>
        <!--when pushed to reply, jQuery must get the reply_to_id otherwise it will reply to author directly-->
        <!--在父元素上设置overflow属性父元素设置overflow：auto；或overflow：hidden；来消除子元素float脱离文档流的问题注意：overflow属性并不是专门用来清除float的-->
        {% if btn%}
        <div style="overflow: hidden;">
            <div style="display: none;" name="reply">{{ element[1] }}</div>
            <div style="display: none;" name="reply_to">{{ element[2] }}</div>
            <a style="float: right;" href="javascript:void(0);" class="btn btn-sm btn-info" name="reply_btn" onclick="insert_submit_form(this)">回复</a>
        </div>
        {% endif %}
    </div>
{% endmacro %}
```
最后，需要写一段JS来展开、销毁回复按钮

```
:::javascript

var insert_submit_form = function (e) {
    var _this = $(e);

    if (_this.attr("status")) {
        //destroy the inline-leave-a-message form
        $("[name='inline-form']").remove();
        _this.attr("class", "btn btn-sm btn-info");
        _this.removeAttr("status");
        _this.html("回复");
    } else {
        //get the id of the comment message
        var reply_id = _this.siblings("[name='reply']").html();
        var reply_to_id = _this.siblings("[name='reply_to']").html();

        //clone DOM
        var fm_html = $("#leave-a-message").clone(true);
        var fm_form = fm_html.find(".form");
        fm_form.attr("name", "inline-form");

        //insert reply_id to form, make reply_id as the new comment's reply_to_id
        fm_form.append('<input type="hidden" name="reply_to_id" value="' + reply_id + '" >');
        var _this_parent = _this.parents().parents(":first");
        _this_parent.append(fm_form[0]);

        //when it's all done, turn btn-info to btn-warning and change the button html
        _this.attr("class", "btn btn-sm btn-warning");
        _this.attr("status", "clicked");
        _this.html("取消");
    }
};
```

<p align="center"><img src="{filename}/images/2017-01-20-li-yong-JinJa-hong-ji-SQLite-CTE-she-ji-lei-si-wang-yi-ping-lun-de-hui-fu-xi-tong-1.png" alt="图-1" style="zoom: 80%"></p>

效果如上，关于搭建第三方评论系统请参考我的另一篇[文章](http://www.kukumalu.cc/shi-yong-issodai-ti-disqusda-jian-ping-lun-xi-tong.html).