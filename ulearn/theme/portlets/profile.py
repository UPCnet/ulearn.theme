from hashlib import sha1
from copy import deepcopy

from Acquisition import aq_inner
from Acquisition import aq_chain
from OFS.Image import Image
from zope.interface import implements
from zope.component import queryUtility
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.security import checkPermission

from plone.app.portlets.portlets import base
from plone.registry.interfaces import IRegistry
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ulearn.core.badges import AVAILABLE_BADGES
from ulearn.core.content.community import ICommunity
from ulearn.core.controlpanel import IUlearnControlPanelSettings

from maxclient import MaxClient
from mrs.max.browser.controlpanel import IMAXUISettings


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
        member_info = pm.getMemberInfo()

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
        portrait = pm.getPersonalPortrait()

        if user.getProperty('fullname') \
           and user.getProperty('fullname') != user.getProperty('username') \
           and user.getProperty('email') \
           and isinstance(portrait, Image):
            return True
        else:
            return False

    def get_badges(self):
        """ Done consistent with an hipotetical badge provider backend """
        # Call to the REST service for the user badges returning a list with the
        # (for example 4 more recent badges or the user selected badges)
        # >>> connect_backpack(self.username.getId(), app="ulearn", sort="user_preference", limit=4)
        # >>> [{"displayName": "Code Whisperer", "id":"codewhisperer", "png": "http://...", "icon": "trophy"}, ]

        badges = deepcopy(AVAILABLE_BADGES)
        if self.has_complete_profile():
            badges[0]['awarded'] = True

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IUlearnControlPanelSettings, check=False)

        thinnkins = self.get_thinnkins()
        if thinnkins:
            if (thinnkins >= int(settings.threshold_winwin1)):
                badges[1]['awarded'] = True
            if (thinnkins >= int(settings.threshold_winwin2)):
                badges[2]['awarded'] = True
            if (thinnkins >= int(settings.threshold_winwin3)):
                badges[3]['awarded'] = True

        return badges

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

    def showEditCommunity(self):
        pm = getToolByName(self.portal(), "portal_membership")
        user = pm.getAuthenticatedMember()

        if not IPloneSiteRoot.providedBy(self.context) and \
           ICommunity.providedBy(self.context) and \
           'Owner' in self.context.get_local_roles_for_userid(user.id):
            return True

    @memoize_contextless
    def get_thinnkins(self, community=False):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        # Pick grant type from settings unless passed as optional argument
        effective_grant_type = settings.oauth_grant_type

        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        username = member.getUserName()
        member = pm.getMemberById(username)
        oauth_token = member.getProperty('oauth_token', None)

        maxclient = MaxClient(url=settings.max_server, oauth_server=settings.oauth_server, grant_type=effective_grant_type)
        maxclient.setActor(username)
        maxclient.setToken(oauth_token)

        if community:
            context_hash = sha1(community.absolute_url()).hexdigest()
            return maxclient.getContextActivities(context=context_hash, count=True)
        else:
            return maxclient.getUserActivities(count=True)

    def get_addable_types(self):
        factories_view = getMultiAdapter((self.context, self.request), name='folder_factories')
        return factories_view.addable_types()


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
