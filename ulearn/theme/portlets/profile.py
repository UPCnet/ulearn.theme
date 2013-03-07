from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from genweb.core.interfaces import IHomePage
from genweb.core.utils import pref_lang
from zope.component import getMultiAdapter


from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _


class IProfilePortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(IProfilePortlet)

    title = _(u'profile', default=u'User profile')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/profile.pt')

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
