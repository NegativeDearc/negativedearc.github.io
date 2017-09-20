---
layout: page
title: Categories
permalink: /categories/
---

<section>

{% for category in site.categories %}
    <li>
    <a href="/{{ category | first | slugize }}/">
        {{ category | first }}
    </a>
    </li>
{% endfor %}

</section>