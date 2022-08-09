from django import template

register = template.Library()


@register.filter("text_normailze")
def text_normailze(value: str):
    return "".join(c for c in value if c.isalnum())


@register.simple_tag
def group_by(value, by):
    value_dict = {}
    for item in value:
        if isinstance(item, dict):
            data = item[by]
        else:
            data = getattr(item, by)
        if data not in value_dict:
            value_dict[data] = []
        value_dict[data].append(item)
    return value_dict


@register.filter("day_with_postfix")
def day_with_postfix(day):
    last = int(list(str(day))[-1])
    day_dict = {
        1: "st",
        2: "nd",
        3: "rd",
    }
    if int(day) > 14:
        try:
            return f"{day}{day_dict[last]}"
        except KeyError:
            pass
    return f"{day}th"
