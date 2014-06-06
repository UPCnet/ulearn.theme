from zope.interface import implements
from zope.security import checkPermission
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from Acquisition import aq_chain

from genweb.core.interfaces import IHomePage
from genweb.core.utils import pref_lang
from zope.component import getMultiAdapter
from ulearn.core.content.community import ICommunity

from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from ulearn.core.interfaces import IDiscussionFolder

import plone.api


class ICommentsPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICommentsPortlet)

    title = _(u'discussion', default=u'Discussion portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/discussion.pt')

    def show_newdiscussion_url(self):
        context = aq_inner(self.context)
        if IHomePage.providedBy(context) or IPloneSiteRoot.providedBy(self.context):
            return False

        if 'Editor' in plone.api.user.get_roles(obj=self.get_community()):
            return True
        else:
            return False

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def newdiscussion_url(self):
        discussion_folder_url = self.get_discussion_folder_url()
        return '{}/++add++ulearn.discussion'.format(discussion_folder_url)

    def get_discussion_folder_url(self):
        community = self.get_community()
        discussion_folder_id = ''
        for obj_id in community.objectIds():
            if IDiscussionFolder.providedBy(community[obj_id]):
                discussion_folder_id = obj_id
        return '{}/{}'.format(self.get_community().absolute_url(), discussion_folder_id)

    def getCommunities(self):
        portal = getSite()
        pc = getToolByName(portal, "portal_catalog")
        communities = pc.searchResults(object_provides=ICommunity.__identifier__)
        return communities

    def is_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return True

        return False


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
