from hashlib import sha1

from Acquisition import aq_inner
from Acquisition import aq_chain
from zope.interface import implements
from zope.component import getMultiAdapter, queryUtility, getUtility
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
from mrs.max.utilities import IMAXClient
from mrs.max.browser.controlpanel import IMAXUISettings

import plone.api


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

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def community_mode(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False

    def get_stats_for(self, query_type):
        current_path = '/'.join(self.context.getPhysicalPath())
        pc = getToolByName(self.portal(), "portal_catalog")
        if query_type == 'documents':
            results = pc.searchResults(portal_type=['Document', 'File'], path={'query': current_path})
        elif query_type == 'links':
            results = pc.searchResults(portal_type=['Link'], path={'query': current_path})
        elif query_type == 'media':
            results = pc.searchResults(portal_type=['Image'], path={'query': current_path})

        return len(results)

    @memoize_contextless
    def get_context_activities(self):
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        username = member.getUserName()
        member = pm.getMemberById(username)
        oauth_token = member.getProperty('oauth_token', None)

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(username)
        maxclient.setToken(oauth_token)

        context_hash = sha1(self.get_community().absolute_url()).hexdigest()
        return maxclient.contexts[context_hash].activities.head()

    def get_all_activities(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        return maxclient.activities.head()

    def get_all_comments(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        return maxclient.activities.comments.head()

    def get_comments_by_context(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        context_hash = sha1(self.get_community().absolute_url()).hexdigest()
        return maxclient.contexts[context_hash].comments.head()

    def get_posts_literal(self):
        literal = plone.api.portal.get_registry_record(name='ulearn.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return 'entrades'


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
