from five import grok

from Products.CMFPlone.interfaces import IPloneSiteRoot

from genweb.theme.browser.views import HomePageBase
from genweb.theme.browser.interfaces import IHomePageView

from ulearn.theme.browser.interfaces import IUlearnTheme


class homePage(HomePageBase):
    """ Override the original homepage as it will be always restricted to auth users """
    grok.implements(IHomePageView)
    grok.context(IPloneSiteRoot)
    grok.require('genweb.authenticated')
    grok.layer(IUlearnTheme)
