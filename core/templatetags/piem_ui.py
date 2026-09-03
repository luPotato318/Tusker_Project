from django import template

register = template.Library()


@register.filter
def score_tier(score):
    value = int(score or 0)
    if value >= 800:
        return "elite"
    if value >= 550:
        return "accelerating"
    if value >= 300:
        return "developing"
    return "starting"


@register.simple_tag
def ranking_badge(position, score):
    return f"#{position} · {score}/1000"
