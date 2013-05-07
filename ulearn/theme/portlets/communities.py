from zope.interface import implements
from zope.security import checkPermission
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from genweb.core.interfaces import IHomePage
from ulearn.core.content.community import ICommunity

from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _


class ICommunitiesNavigation(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICommunitiesNavigation)

    title = _(u'communities', default=u'Communities portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/communities.pt')

    def portal_url(self):
        return getSite().absolute_url()

    def showCreateCommunity(self):
        if IHomePage.providedBy(self.context):
            return True

    def showEditCommunity(self):
        if not IPloneSiteRoot.providedBy(self.context) and \
           ICommunity.providedBy(self.context) and \
           checkPermission('cmf.RequestReview', self.context):
            return True

    def getCommunities(self):
        portal = getSite()
        pc = getToolByName(portal, "portal_catalog")
        pm = getToolByName(portal, "portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()
        communities = pc.searchResults(object_provides=ICommunity.__identifier__, favoritedBy=current_user)
        return communities

    def getCommunityMembers(self, community):
        if community.subscribed_items < 100:
            return community.subscribed_items
        else:
            return '+99'

    def get_community_title(self, title):
        if len(title) > 20:
            return title[:20] + '...'
        else:
            return title


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
