from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from plone.app.portlets.portlets import base
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ulearn.core.badges import PROFILE_COMPLETE_BADGE


class IProfilePortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(IProfilePortlet)

    title = _(u'profile', default=u'User profile')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/profile.pt')

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def username(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        return pm.getAuthenticatedMember()

    def fullname(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        userid = pm.getAuthenticatedMember()
        member_info = pm.getMemberInfo(userid)
        if member_info:
            fullname = member_info.get('fullname', '')
        else:
            fullname = None
        if fullname:
            return fullname
        else:
            return userid

    def get_portrait(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        return pm.getPersonalPortrait().absolute_url()

    def has_complete_profile(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getAuthenticatedMember()
        if user.getProperty('fullname') \
           and user.getProperty('email') \
           and user.getProperty('portrait'):
            return True
        else:
            return False

    def get_badges(self):
        """ Done consistent with an hipotetical badge provider backend """
        # Call to the REST service for the user badges returning a list with the
        # (for example 4 more recent badges or the user selected badges)
        # >>> connect_backpack(self.username.getId(), app="ulearn", sort="user_preference", limit=4)
        # >>> [{"displayName": "Code Whisperer", "id":"codewhisperer", "png": "http://...", "icon": "trophy"}, ]

        badges = []
        if self.has_complete_profile():
            badges.append(PROFILE_COMPLETE_BADGE)
        return []


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
