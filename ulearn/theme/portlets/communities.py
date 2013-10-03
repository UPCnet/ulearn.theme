from zope.interface import implements
from zope.component.hooks import getSite
from zope.component import queryUtility
from zope.security import checkPermission

from plone.app.portlets.portlets import base
from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.core.interfaces import IHomePage
from ulearn.core.content.community import ICommunity
from ulearn.core.controlpanel import IUlearnControlPanelSettings


class ICommunitiesNavigation(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICommunitiesNavigation)

    title = _(u'communities', default=u'Communities portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/communities.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def showCreateCommunity(self):
        """The Contributor role is assumed that will be applied at the front-
           page object.
        """
        if IHomePage.providedBy(self.context) and \
           checkPermission('ulearn.addCommunity', self.context):
            return True

    def showEditCommunity(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getAuthenticatedMember()

        if not IPloneSiteRoot.providedBy(self.context) and \
           ICommunity.providedBy(self.context) and \
           ('Manager' in user.getRoles() or
           'WebMaster' in user.getRoles() or
           'Site Administrator' in user.getRoles() or
           'Owner' in user.getRoles()):
            return True

    def getCommunities(self):
        portal = self.portal()
        pc = getToolByName(portal, "portal_catalog")
        pm = getToolByName(portal, "portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()
        communities = pc.searchResults(object_provides=ICommunity.__identifier__,
                                       favoritedBy=current_user,
                                       sort_on="subscribed_items",
                                       sort_order="reverse")
        return communities

    def getCommunityMembers(self, community):
        if community.subscribed_items < 100:
            return community.subscribed_items
        else:
            return '+99'

    def get_community_title(self, title):
        if len(title) > 18:
            return title[:18] + '...'
        else:
            return title

    def get_campus_url(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)
        return settings.campus_url


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
