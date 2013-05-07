from hashlib import sha1

from Acquisition import aq_inner
from Acquisition import aq_chain
from zope.interface import implements
from zope.component import getMultiAdapter, queryUtility
from zope.component.hooks import getSite

from plone.app.portlets.portlets import base
from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ulearn.core.badges import AVAILABLE_BADGES
from ulearn.core.content.community import ICommunity
from ulearn.core.controlpanel import IUlearnControlPanelSettings

from maxclient import MaxClient
from mrs.max.browser.controlpanel import IMAXUISettings


class IStatsPortlet(IPortletDataProvider):
    """ A portlet which can render the community stats information """


class Assignment(base.Assignment):
    implements(IStatsPortlet)

    title = _(u'stats', default=u'Stats')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/stats.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def get_stats_for(self, query_type):
        current_path = '/'.join(self.context.getPhysicalPath())
        pc = getToolByName(self.portal(), "portal_catalog")
        if query_type == 'documents':
            results = pc.searchResults(portal_type=['Document', 'File'], path={'query': current_path})
        elif query_type == 'links':
            results = pc.searchResults(portal_type=['Link'], path={'query': current_path})
        elif query_type == 'photos':
            results = pc.searchResults(portal_type=['Image'], path={'query': current_path})

        return len(results)


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
