from hashlib import sha1
from plone import api
from Acquisition import aq_inner
from Acquisition import aq_chain
from zope.interface import implements
from zope.component import getMultiAdapter, queryUtility, getUtility
from zope.component.hooks import getSite

from plone.app.portlets.portlets import base
from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.core.interfaces import IHomePage
from ulearn.core.badges import AVAILABLE_BADGES
from ulearn.core.content.community import ICommunity
from ulearn.core.controlpanel import IUlearnControlPanelSettings

from maxclient import MaxClient
from mrs.max.utilities import IMAXClient
from mrs.max.browser.controlpanel import IMAXUISettings
from zope.security import checkPermission

from genweb.core.utils import get_safe_member_by_id


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
        if IHomePage.providedBy(self.context):
            portal = api.portal.get()
            current_path = '/'.join(portal.getPhysicalPath())
        else:
            current_path = '/'.join(self.context.getPhysicalPath())
        pc = getToolByName(self.portal(), "portal_catalog")
        if query_type == 'documents':
            results = pc.searchResults(portal_type=['Document', 'File'], path={'query': current_path})
        elif query_type == 'links':
            results = pc.searchResults(portal_type=['Link'], path={'query': current_path})
        elif query_type == 'media':
            results = pc.searchResults(portal_type=['Image', 'Video'], path={'query': current_path})

        return len(results)

    @memoize_contextless
    def get_context_activities(self):
        current_user = api.user.get_current()
        oauth_token = current_user.getProperty('oauth_token', None)

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(current_user.id)
        maxclient.setToken(oauth_token)

        context_hash = sha1(self.get_community().absolute_url()).hexdigest()

        try:
            activities = maxclient.contexts[context_hash].activities.head()
        except:
            activities = 'ND'

        return activities

    def get_all_activities(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        try:
            all_activities = maxclient.activities.head()
        except:
            all_activities = 'ND'

        return all_activities

    def get_all_comments(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        try:
            all_comments = maxclient.activities.comments.head()
        except:
            all_comments = 'ND'

        return all_comments

    def get_comments_by_context(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        context_hash = sha1(self.get_community().absolute_url()).hexdigest()

        try:
            comments = maxclient.contexts[context_hash].comments.head()
        except:
            comments = 'ND'

        return comments

    def get_posts_literal(self):
        literal = api.portal.get_registry_record(name='ulearn.core.controlpanel.IUlearnControlPanelSettings.people_literal')
        if literal == 'thinnkers':
            return 'thinnkins'
        else:
            return 'entrades'

    def show_stats(self):
        """ The genweb.webmaster can see stats.
        """
        if checkPermission('genweb.webmaster', self.context):
            return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
