from hashlib import sha1
from plone import api
from zope.interface import implements
from zope.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_chain

from zope.component import getMultiAdapter, queryUtility

from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _

from ulearn.core.content.community import ICommunity

from maxclient import MaxClient
from mrs.max.browser.controlpanel import IMAXUISettings


class IThinnkersPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(IThinnkersPortlet)

    title = _(u'thinnkers', default=u'Thinnkers portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/thinnkers.pt')

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

    def get_people_literal(self):
        return api.portal.get_registry_record(name='ulearn.core.controlpanel.IUlearnControlPanelSettings.people_literal')

    def get_seemoreusers_literal(self):
        return 'seemoreusers_{}'.format(self.get_people_literal())

    def get_thinnkers(self, community=False):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        # Pick grant type from settings unless passed as optional argument
        effective_grant_type = settings.oauth_grant_type

        current_user = api.user.get_current()
        oauth_token = current_user.getProperty('oauth_token', None)

        maxclient = MaxClient(url=settings.max_server, oauth_server=settings.oauth_server, grant_type=effective_grant_type)
        maxclient.setActor(current_user.id)
        maxclient.setToken(oauth_token)

        if community:
            context_hash = sha1(community.absolute_url()).hexdigest()
            context_last_authors = maxclient.getContextLastAuthors(context=context_hash, limit=8)
            if context_last_authors:
                return context_last_authors[:8]
            else:
                return []
        else:
            context_last_authors = maxclient.getTimelineLastAuthors(limit=8)
            if context_last_authors:
                return context_last_authors[:8]
            else:
                return []


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
