from OFS.Image import Image

from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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

    def __call__(self):
        pm = getToolByName(self, 'portal_membership')
        portrait = pm.getPersonalPortrait(self.username)
        if isinstance(portrait, Image):
            self.request.response.addHeader('Content-Type', portrait.content_type)
            return portrait.data
        else:
            self.request.response.addHeader('Content-Type', portrait.getContentType())
            return portrait._readFile(portrait)
