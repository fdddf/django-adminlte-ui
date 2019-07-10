import itertools
from django.contrib.admin.views.main import (
    ALL_VAR, ORDER_VAR, PAGE_VAR, SEARCH_VAR,
)
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.template import Library
from django.template.loader import get_template
import urllib.parse

register = Library()

DOT = '.'


@register.simple_tag
def adminlte_paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == DOT:
        # <li class="paginate_button active"><a href="#" aria-controls="example2" data-dt-idx="3" tabindex="0">{}</a></li>'
        return format_html(
            '<li class="paginate_button"><a href="javascript:void(0);" aria-controls="example2" data-dt-idx="3" tabindex="0">… </a></li>')
    elif i == cl.page_num:
        return format_html(
            '<li class="paginate_button active"><a href="javascript:void(0);" aria-controls="example2" data-dt-idx="3" tabindex="0">{}</a></li>',
            i + 1)
    else:
        return format_html(
            '<li class="paginate_button "><a href="{}" {} aria-controls="example2" data-dt-idx="3" tabindex="0">{}</a></li>',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(
                ' class="end"' if i == cl.paginator.num_pages - 1 else ''),
            i + 1,
        )
