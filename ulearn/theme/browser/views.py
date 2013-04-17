from five import grok

from plone.batching import Batch

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from genweb.theme.browser.views import HomePageBase
from genweb.theme.browser.interfaces import IHomePageView

from ulearn.theme.browser.interfaces import IUlearnTheme


class homePage(HomePageBase):
    """ Override the original homepage as it will be always restricted to auth users """
    grok.implements(IHomePageView)
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.layer(IUlearnTheme)


class baseCommunities(grok.View):
    grok.baseclass()

    def update(self):
        self.favorites = self.get_favorites()

    def get_communities(self):
        pc = getToolByName(self.context, "portal_catalog")
        results = pc.searchResults(portal_type="ulearn.community")
        batch = Batch(results, size=2, orphan=10)
        return batch

    def is_community_manager(self, community):
        pm = getToolByName(self.context, "portal_membership")
        current_user = pm.getAuthenticatedMember().getUserName()
        return current_user == community.Creator

    def get_favorites(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()

        results = pc.unrestrictedSearchResults(favoritedBy=current_user)
        return [favorites.id for favorites in results]

    def get_star_class(self, community):
        return community.id in self.favorites and 'fa-icon-star' or 'fa-icon-star-empty'


class communities(baseCommunities):
    """ The list of communities """
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.layer(IUlearnTheme)


class communitiesAJAX(baseCommunities):
    """ The list of communities via AJAX """
    grok.name('communities-ajax')
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.template('communities_ajax')
    grok.layer(IUlearnTheme)
