from copy import deepcopy
from OFS.Image import Image

from zope.interface import implements
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.publisher.interfaces import IPublishTraverse, NotFound

from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from mrs.max.utilities import IMAXClient
from ulearn.core.badges import AVAILABLE_BADGES
from ulearn.core.controlpanel import IUlearnControlPanelSettings


class userProfile(BrowserView):
    """ Return an user profile ../profile/{username} """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(userProfile, self).__init__(context, request)
        self.username = None

    def publishTraverse(self, request, name):
        if self.username is None:  # ../profile/username
            self.username = name
        else:
            raise NotFound(self, name, request)
        return self

    index = ViewPageTemplateFile('views_templates/user_profile.pt')

    def __call__(self):
        return self.index()

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

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

    def get_member_data(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        user = pm.getMemberById(self.username)
        return user

    def user_properties(self):
        member_data = self.get_member_data()
        return {'fullname': member_data.getProperty('fullname'),
                'email': member_data.getProperty('email'),
                'home_page': member_data.getProperty('home_page'),
                'description': member_data.getProperty('description'),
                'twitter_username': member_data.getProperty('twitter_username'),
                'location': member_data.getProperty('location'),
                'telefon': member_data.getProperty('telefon'),
                'ubicacio': member_data.getProperty('ubicacio'),
                }

    def get_badges(self):
        """ Done consistent with an hipotetical badge provider backend """
        # Call to the REST service for the user badges returning a list with the
        # (for example 4 more recent badges or the user selected badges)
        # >>> connect_backpack(self.username.getId(), app="ulearn", sort="user_preference", limit=4)
        # >>> [{"displayName": "Code Whisperer", "id":"codewhisperer", "png": "http://...", "icon": "trophy"}, ]

        badges = deepcopy(AVAILABLE_BADGES)
        if self.has_complete_profile():
            badges[0]['awarded'] = True

        registry = getUtility(IRegistry)
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

    @memoize_contextless
    def get_thinnkins(self):
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        return maxclient.people[self.username].activities.head()
