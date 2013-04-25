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

from genweb.core.utils import pref_lang
from genweb.core.interfaces import IHomePage


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

    def getPortrait(self):
        pm = getToolByName(self.portal(), 'portal_membership')
        return pm.getPersonalPortrait().absolute_url()

    def getHomepage(self):
        page = {}
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                  Language=pref_lang())
        page['body'] = result[0].CookedBody()

        return page


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
