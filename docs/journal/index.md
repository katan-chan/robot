---
title: Spider Robot Journal
---

# Spider Robot Journal

A four-legged spider robot with 12 servos, simulated in MuJoCo, designed by one person together with AI agents. The robot is the backdrop. The real story is what happens when a human and agents build a hardware project together: what the agents got wrong, what the human got wrong, and how each problem was solved.

Nothing is hidden. Every decision, note and line of code lives in the [public repository](https://github.com/katan-chan/robot).

## Posts

<ul>
{% assign posts = site.pages | where_exp: "p", "p.path contains 'journal/posts/'" | sort: "date" | reverse %}
{% for p in posts %}
  <li>{{ p.date | date: "%Y-%m-%d" }} - <a href="{{ p.url | relative_url }}">{{ p.title }}</a></li>
{% endfor %}
</ul>
