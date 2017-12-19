# -*- coding: utf-8 -*-
import re
from five import grok
from cgi import escape
from Acquisition import aq_inner
from Acquisition import aq_chain
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.component import getUtility
from zope.security import checkPermission

from plone.memoize.view import memoize_contextless
from plone.memoize import forever

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot

from souper.soup import get_soup
from souper.soup import Record

from repoze.catalog.query import Eq

from plone.app.layout.viewlets.common import TitleViewlet, ManagePortletsFallbackViewlet
from plone.app.layout.viewlets.interfaces import IHtmlHead, IPortalTop, IPortalHeader, IAboveContent, IBelowContent
from plone.app.layout.viewlets.interfaces import IPortalFooter, IAboveContentTitle
from plone.registry.interfaces import IRegistry
from plone.dexterity.interfaces import IDexterityContent
from ulearn.core.controlpanel import IUlearnControlPanelSettings

from genweb.core.utils import genweb_config
from genweb.core.utils import pref_lang
from genweb.core.utils import get_safe_member_by_id
from genweb.theme.browser.viewlets import gwPersonalBarViewlet
from genweb.theme.browser.viewlets import gwManagePortletsFallbackViewletMixin
from genweb.core.browser.viewlets import gwCSSViewletManager
from genweb.core.browser.viewlets import baseResourcesViewlet

from ulearn.core.content.community import ICommunity
from ulearn.core.interfaces import IDocumentFolder
from ulearn.core.interfaces import ILinksFolder
from ulearn.core.interfaces import IPhotosFolder
from ulearn.core.interfaces import IEventsFolder
from ulearn.core.interfaces import IDiscussionFolder
from ulearn.theme.browser.interfaces import IUlearnTheme

from zope.component import queryUtility

import datetime
from plone import api

grok.context(Interface)


class gwCSSViewlet(baseResourcesViewlet):
    """ This is the uLearn CSS viewlet. """
    grok.context(Interface)
    grok.viewletmanager(gwCSSViewletManager)
    grok.layer(IUlearnTheme)

    resource_type = 'css'
    current_egg_name = 'ulearn.theme'


class viewletBase(grok.Viewlet):
    grok.baseclass()

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def genweb_config(self):
        return genweb_config()

    def pref_lang(self):
        """ Extracts the current language for the current user
        """
        lt = getToolByName(self.portal(), 'portal_languages')
        return lt.getPreferredLanguage()


class folderBar(viewletBase):
    grok.name('ulearn.folderbar')
    grok.template('folderbar')
    grok.viewletmanager(IAboveContent)
    grok.layer(IUlearnTheme)

    def update(self):
        context = aq_inner(self.context)
        self.folder_type = ''
        for obj in aq_chain(context):
            if IDocumentFolder.providedBy(obj):
                self.folder_type = 'documents'
                break
            if ILinksFolder.providedBy(obj):
                self.folder_type = 'links'
                break
            if IPhotosFolder.providedBy(obj):
                self.folder_type = 'photos'
                break
            if IEventsFolder.providedBy(obj):
                self.folder_type = 'events'
                break
            if IDiscussionFolder.providedBy(obj):
                self.folder_type = 'discussion'
                break
            if ICommunity.providedBy(obj):
                self.folder_type = 'community'
                break

    def bubble_class(self, bubble):
        if self.folder_type == 'events' or \
           self.folder_type == 'discussion':
            span = 'span4'
        else:
            span = 'span6'

        # if bubble == 'events' or \
        #    bubble == 'discussion':
        #     span = 'span3'

        if bubble == self.folder_type:
            return 'active bubble top {}'.format(span)
        elif bubble == 'documents' and 'photos' == self.folder_type:
            return 'active bubble top {}'.format(span)
        else:
            return 'bubble top {}'.format(span)

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def render_viewlet(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True
        return False


class ulearnPersonalBarViewlet(gwPersonalBarViewlet):
    """ Done without jbot as it was failing sometimes randomly """
    grok.name('genweb.personalbar')
    grok.viewletmanager(IPortalTop)
    grok.layer(IUlearnTheme)

    index = ViewPageTemplateFile('viewlets_templates/personal_bar.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.navigation_root_url = self.portal_state.navigation_root_url()

        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')

        self.user_actions = context_state.actions('user')
        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
            member = self.portal_state.member()
            userid = member.getId()

            self.homelink_url = "%s/useractions" % self.navigation_root_url

            # Use the local catalog instead of getMemberById
            member_info = get_safe_member_by_id(userid)
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid

    def is_upc_site(self):
        """ Check if the site is using LDAP UPC for show the
            correct change password link
        """

        acl_users = api.portal.get_tool(name='acl_users')
        if 'ldapUPC' in acl_users:
            return True
        else:
            return False

    def quicklinks(self):
        """ Return de quicklinks for language
        """
        lang = pref_lang()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        text = None
        if settings.quicklinks_literal is not None:
            for item in settings.quicklinks_literal:
                if lang in item['language']:
                    text = item['text']
                    break

        items = []
        if settings.quicklinks_table is not None:
            for item in settings.quicklinks_table:
                if lang in item['language']:
                    items.append(item)

        if len(items) > 0:
            quicklinks_show = True
        else:
            quicklinks_show = False

        dades = {'quicklinks_literal': text,
                 'quicklinks_icon': settings.quicklinks_icon,
                 'quicklinks_table': items,
                 'quicklinks_show': quicklinks_show,
                 }

        return dades

    def canGestion(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'gestion' in portal:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion'])
            if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles or self.canGestionarMenu() or self.canGestionarHeader() or self.canGestionarFooter() or self.canGestionarNoticies() or self.canGestionarEstadistiques():
                return True

        return False

    def canGestionarDirectori(self, directori):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'gestion' in portal and directori in portal['gestion']:
            roles = api.user.get_roles(username=current.id, obj=portal['gestion'][directori])
            if 'Editor' in roles or 'Contributor' in roles or 'Reviewer' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True

        return False

    def canGestionarMenu(self):
        return self.canGestionarDirectori('menu')

    def canGestionarHeader(self):
        return self.canGestionarDirectori('header')

    def canGestionarFooter(self):
        return self.canGestionarDirectori('footer')

    def canGestionarNoticies(self):
        current = api.user.get_current()
        portal = api.portal.get()
        if 'news' in portal:
            roles = api.user.get_roles(username=current.id, obj=portal['news'])
            if 'Editor' in roles or 'Contributor' in roles or 'WebMaster' in roles or 'Manager' in roles:
                return True
        return False

    def canGestionarEstadistiques(self):
        current = api.user.get_current()
        portal = api.portal.get()
        roles = api.user.get_roles(username=current.id, obj=portal)
        if 'WebMaster' in roles or 'Manager' in roles:
            return True
        return False

    def genera_menu_enlaces(self, language):
        """ Genera el menu de enlaces segun el idioma que tenga definido el
            usuario en su perfil
        """
        portal = api.portal.get()
        if 'gestion' in portal and 'menu' in portal['gestion'] and language in portal['gestion']['menu']:
            menu = portal['gestion']['menu'][language]
            path_language = "/".join(menu.getPhysicalPath())

            catalog = api.portal.get_tool(name='portal_catalog')
            folders = catalog(portal_type=('Folder', 'privateFolder'),
                              review_state='intranet',
                              path={'query': path_language, 'depth': 1},
                              sort_on="getObjPositionInParent")

            carpetes = {}
            for folder in folders:
                path = folder.getPath()
                carpeta = {'id': folder.id,
                           'title': folder.getObject().title,
                           'url': folder.getURL(),
                           'links': []
                           }
                carpetes[path] = carpeta

            res = catalog(portal_type='Link',
                          review_state='intranet',
                          path={'query': path_language, 'depth': 2},
                          sort_on="getObjPositionInParent")

            links = []
            links.extend(res)
            for link in links:
                obj = link.getObject()
                link_parent_path = "/".join(obj.__parent__.getPhysicalPath())
                info = {'id': obj.id,
                        'title': obj.title,
                        'url': obj.remoteUrl,
                        'new_window': obj.open_link_in_new_window,
                        }
                try:
                    carpetes[link_parent_path]['links'].append(info)
                except:
                    pass

            return carpetes
        else:
            return {}

    def menu_enlaces(self):
        """ Devuelve el menu de enlaces segun el idioma que tenga definido el
            usuario en su perfil
        """
        current = api.user.get_current()
        user_language = current.getProperty('language')
        if user_language == '':
            lt = getToolByName(self.portal(), 'portal_languages')
            user_language = lt.getPreferredLanguage()
            current.setMemberProperties({'language': user_language})

        portal = api.portal.get()
        soup_menu = get_soup('menu_soup', portal)
        exist = [r for r in soup_menu.query(Eq('id_menusoup', user_language))]
        if not exist:
            dades = self.genera_menu_enlaces(user_language)
            record = Record()
            record.attrs['id_menusoup'] = user_language
            record.attrs['dades'] = dades.values()
            soup_menu.add(record)
            soup_menu.reindex()
            return dades.values()
        else:
            return exist[0].attrs['dades']

    def getUserId(self):
        current = api.user.get_current()
        return current.id


class gwHeader(viewletBase):
    grok.name('genweb.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IUlearnTheme)

    def get_info_servei(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)
        return settings.info_servei

    def canHeaderImatge(self):
        portal = api.portal.get()
        if 'gestion' in portal:
            if 'header' in portal['gestion']:
                path = '/'.join(portal.getPhysicalPath()) + "/gestion/header"
                catalog = api.portal.get_tool('portal_catalog')
                brains = catalog(portal_type=('Image'),
                                 sort_on='getObjPositionInParent',
                                 sort_order='ascending',
                                 sort_limit=1,
                                 path={'query': path, 'depth': 1})
                if brains:
                    return brains[0].getObject().id
        return False


class gwFooter(viewletBase):
    grok.name('genweb.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IUlearnTheme)

    @forever.memoize
    def get_current_year(self):
        return datetime.datetime.now().year

    def getPersonalizedFooter(self):
        portal = api.portal.get()
        if 'gestion' in portal:
            if 'footer' in portal['gestion']:
                path = '/'.join(portal.getPhysicalPath()) + '/gestion/footer'
                catalog = api.portal.get_tool('portal_catalog')
                brains = catalog(portal_type=('Document'),
                                 sort_on='getObjPositionInParent',
                                 sort_order='ascending',
                                 sort_limit=1,
                                 path={'query': path, 'depth': 1})
                if brains:
                    return brains[0].getObject().text
        return None


class TitleViewlet(TitleViewlet, viewletBase):
    grok.context(Interface)
    grok.name('plone.htmlhead.title')
    grok.viewletmanager(IHtmlHead)
    grok.layer(IUlearnTheme)

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        portal_title = escape(safe_unicode(portal_state.navigation_root_title()))

        genweb_title = getattr(self.genweb_config(), 'html_title_%s' % self.pref_lang(), 'uLearn Comunidades')
        if not genweb_title:
            genweb_title = 'uLearn Comunidades'
        genweb_title = escape(safe_unicode(re.sub(r'(<.*?>)', r'', genweb_title)))

        # marca_UPC = escape(safe_unicode(u"UPC. Universitat Politècnica de Catalunya · BarcelonaTech"))

        if page_title == portal_title:
            self.site_title = u"%s" % (genweb_title)
        else:
            self.site_title = u"%s &mdash; %s" % (page_title, genweb_title)


class socialtoolsViewlet(viewletBase):
    grok.name('genweb.socialtools')
    grok.template('socialtools')
    grok.viewletmanager(IAboveContentTitle)
    grok.layer(IUlearnTheme)


class uLearnManagePortletsFallbackViewletForPloneSiteRoot(gwManagePortletsFallbackViewletMixin, ManagePortletsFallbackViewlet, viewletBase):
    """ The override for the manage_portlets_fallback viewlet for IPloneSiteRoot
    """
    grok.context(IPloneSiteRoot)
    grok.name('plone.manage_portlets_fallback')
    grok.viewletmanager(IBelowContent)
    grok.layer(IUlearnTheme)


class favoriteViewlet(viewletBase):
    grok.name('genweb.favorite')
    grok.template('favorite')
    grok.context(IDexterityContent)
    grok.viewletmanager(IAboveContentTitle)
    grok.layer(IUlearnTheme)

    def get_star_class(self):
        pm = getToolByName(self.context, "portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()

        if current_user in self.context._favoritedBy:
            return 'fa fa-star'
        else:
            return 'fa fa-star-o'
