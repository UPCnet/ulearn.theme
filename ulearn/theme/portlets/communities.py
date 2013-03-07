from zope.interface import implements
from zope.security import checkPermission
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from genweb.core.interfaces import IHomePage
from genweb.core.utils import pref_lang
from zope.component import getMultiAdapter
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

    def showCreateCommunity(self):
        if IHomePage.providedBy(self.context):
            return True

    def showEditCommunity(self):
        if not IPloneSiteRoot.providedBy(self.context) and \
           ICommunity.providedBy(self.context) and \
           checkPermission('cmf.RequestReview', self.context):
            return True


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
