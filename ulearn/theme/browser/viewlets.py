# -*- coding: utf-8 -*-
import re
from five import grok
from cgi import escape
from Acquisition import aq_inner
from Acquisition import aq_chain
from AccessControl import getSecurityManager
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from plone.memoize.view import memoize_contextless

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import PersonalBarViewlet, GlobalSectionsViewlet, PathBarViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet, TitleViewlet, ManagePortletsFallbackViewlet
from plone.app.layout.viewlets.interfaces import IHtmlHead, IPortalTop, IPortalHeader, IAboveContent, IBelowContent
from plone.app.layout.viewlets.interfaces import IPortalFooter, IAboveContentTitle
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.ATContentTypes.interface.news import IATNewsItem
from genweb.core.adapters import IImportant

from genweb.core.interfaces import IHomePage
from genweb.theme.browser.interfaces import IHomePageView
from genweb.core.utils import genweb_config, havePermissionAtRoot, pref_lang
from genweb.theme.browser.viewlets import gwPersonalBarViewlet
from genweb.theme.browser.interfaces import IGenwebTheme

from ulearn.core.content.community import ICommunity
from ulearn.core.interfaces import IDocumentFolder
from ulearn.core.interfaces import ILinksFolder
from ulearn.core.interfaces import IPhotosFolder
from ulearn.core.interfaces import IEventsFolder
from ulearn.core.interfaces import IDiscussionFolder
from ulearn.theme.browser.interfaces import IUlearnTheme

import plone.api

grok.context(Interface)


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
            span = 'span2'
        else:
            span = 'span3'

        if bubble == 'events' or \
           bubble == 'discussion':
            span = 'span3'

        if bubble == self.folder_type:
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

    def is_upc_site(self):
        """ Check if the site is using LDAP UPC for show the
            correct change password link
        """

        acl_users = plone.api.portal.get_tool(name='acl_users')
        if 'ldapUPC' in acl_users:
            return True
        else:
            return False


class gwHeader(viewletBase):
    grok.name('genweb.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IUlearnTheme)


# class gwImportantNews(viewletBase):
#     grok.name('genweb.important')
#     grok.context(IATNewsItem)
#     grok.template('important')
#     grok.viewletmanager(IAboveContentTitle)
#     grok.layer(IGenwebTheme)

#     def permisos_important(self):
#         #TODO: Comprovar que l'usuari tingui permisos per a marcar com a important
#         return not IImportant(self.context).is_important and getSecurityManager().checkPermission("plone.app.controlpanel.Overview", self.portal)

#     def permisos_notimportant(self):
#         #TODO: Comprovar que l'usuari tingui permisos per a marcar com a notimportant
#         return IImportant(self.context).is_important and getSecurityManager().checkPermission("plone.app.controlpanel.Overview", self.portal)

#     def update(self):
#         form = self.request.form
#         if 'genweb.theme.viewlet.marcar_important' in form:
#             IImportant(self.context).is_important = True
#         if 'genweb.theme.viewlet.marcar_notimportant' in form:
#             IImportant(self.context).is_important = False


# class gwGlobalSectionsViewlet(GlobalSectionsViewlet, viewletBase):
#     grok.name('genweb.globalsections')
#     grok.viewletmanager(IPortalTop)
#     grok.layer(IGenwebTheme)

#     index = ViewPageTemplateFile('viewlets_templates/sections.pt')

#     def show_menu(self):
#         return not self.genweb_config().treu_menu_horitzontal and self.portal_tabs


# class gwPathBarViewlet(PathBarViewlet, viewletBase):
#     grok.name('genweb.pathbar')
#     grok.viewletmanager(IPortalTop)
#     grok.layer(IGenwebTheme)

#     index = ViewPageTemplateFile('viewlets_templates/path_bar.pt')

#     def paginaPrincipal(self):
#         #TODO: Comprovar que no sigui la Pàgina Principal
#         return IHomePageView.providedBy(self.view)


class gwFooter(viewletBase):
    grok.name('genweb.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IUlearnTheme)


# class gwSearchViewletManager(grok.ViewletManager):
#     grok.context(Interface)
#     grok.name('genweb.search_manager')


# class gwSearchViewlet(SearchBoxViewlet, viewletBase):
#     grok.context(Interface)
#     grok.viewletmanager(gwSearchViewletManager)
#     grok.layer(IGenwebTheme)

#     render = ViewPageTemplateFile('viewlets_templates/searchbox.pt')


# class gwManagePortletsFallbackViewlet(ManagePortletsFallbackViewlet, viewletBase):
#     """ The override for the manage_portlets_fallback viewlet for IPloneSiteRoot
#     """
#     grok.context(IPloneSiteRoot)
#     grok.name('plone.manage_portlets_fallback')
#     grok.viewletmanager(IBelowContent)
#     grok.layer(IGenwebTheme)

#     render = ViewPageTemplateFile('viewlets_templates/manage_portlets_fallback.pt')

#     def getPortletContainerPath(self):
#         context = aq_inner(self.context)
#         pc = getToolByName(context, 'portal_catalog')
#         result = pc.searchResults(object_provides=IHomePage.__identifier__,
#                                   Language=pref_lang())
#         if result:
#             return result[0].getURL()
#         else:
#             # If this happens, it's bad. Implemented as a fallback
#             return context.absolute_url()

#     def managePortletsURL(self):
#         return "%s/%s" % (self.getPortletContainerPath(), '@@manage-homeportlets')

#     def available(self):
#         secman = getSecurityManager()
#         if secman.checkPermission('Portlets: Manage portlets', self.context):
#             return True
#         else:
#             return False


class TitleViewlet(TitleViewlet, viewletBase):
    grok.context(Interface)
    grok.name('plone.htmlhead.title')
    grok.viewletmanager(IHtmlHead)
    grok.layer(IUlearnTheme)

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
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
