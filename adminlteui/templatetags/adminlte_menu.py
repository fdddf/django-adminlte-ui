import logging

import django
from django import template
from django.contrib.admin import AdminSite
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from adminlteui.templatetags.adminlte_options import get_adminlte_option
from adminlteui.models import Menu

try:
    from django.urls import reverse, resolve
except:
    from django.core.urlresolvers import reverse, resolve

register = template.Library()

if django.VERSION < (1, 9):
    simple_tag = register.assignment_tag
else:
    simple_tag = register.simple_tag


def get_reverse_link(link):
    if not link or '/' in link:
        return link

    try:
        return reverse(link)
    except Exception as e:
        return None


def get_custom_menu(request):
    """
    use content_type and user.permission control the menu

    `label:model`

    :param request:
    :return:lkkl
    """
    # all_permissions = request.user.get_all_permissions()
    menus = Menu.objects.filter(valid=1)
    # def recurse_node(node):
    #     apps = []
    #     context = {}
    #     if not node.valid:
    #         return
    #     for child in node.get_children():
    #         return recurse_node(child)
    #
    #     context['name'] = node.name
    #     context['icon'] = node.icon
    #     context['models'] = apps
    #     if node.link_type in (0, 1):
    #         context['admin_url'] = get_reverse_link(node.link)
    #     return node
    return menus


@simple_tag(takes_context=True)
def get_menu(context, request):
    """
    :type request: WSGIRequest
    """
    if not isinstance(request, HttpRequest):
        return None

    use_custom_menu = get_adminlte_option('USE_CUSTOM_MENU')
    if use_custom_menu.get('USE_CUSTOM_MENU',
                           '0') == '1' and use_custom_menu.get('valid') is True:
        return get_custom_menu(request), True

    # Django 1.9+
    available_apps = context.get('available_apps')
    if not available_apps:

        # Django 1.8 on app index only
        available_apps = context.get('app_list')

        # Django 1.8 on rest of the pages
        if not available_apps:
            try:
                from django.contrib import admin
                template_response = get_admin_site(request.current_app).index(
                    request)
                available_apps = template_response.context_data['app_list']
            except Exception:
                pass
    if not available_apps:
        logging.warn('adminlteui was unable to retrieve apps list for menu.')

    for app in available_apps:
        if app.get('app_label') == 'django_admin_settings':
            app.get('models').insert(0,
                                     {
                                         'name': _('General Option'),
                                         'object_name': 'Options',
                                         'perms':
                                             {
                                                 'add': True,
                                                 'change': True,
                                                 'delete': True,
                                                 'view': True
                                             },
                                         'admin_url': reverse(
                                             'admin:general_option'),
                                         'view_only': False
                                     }
                                     )
    # return MenuManager(available_apps, context, request)
    return available_apps, False


def get_admin_site(current_app):
    """
    Method tries to get actual admin.site class, if any custom admin sites
    were used. Couldn't find any other references to actual class other than
    in func_closer dict in index() func returned by resolver.
    """
    try:
        resolver_match = resolve(reverse('%s:index' % current_app))
        # Django 1.9 exposes AdminSite instance directly on view function
        if hasattr(resolver_match.func, 'admin_site'):
            return resolver_match.func.admin_site

        for func_closure in resolver_match.func.__closure__:
            if isinstance(func_closure.cell_contents, AdminSite):
                return func_closure.cell_contents
    except:
        pass
    from django.contrib import admin
    return admin.site


@simple_tag(takes_context=True)
def resolve_menu_link(context, request):
    menu = context.get('node')
    if menu.is_leaf_node() and menu.link_type in (0, 1) and menu.link:
            return get_reverse_link(menu.link)
    return 'javascript:void();'
