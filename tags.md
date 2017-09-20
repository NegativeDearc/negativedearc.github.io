---
layout: page
title: Tags
permalink: /tags/
---

<section>

{% for tag in site.tags %}
				
	<li>{{ tag | first }}</li>
	
{% endfor %}

</section>