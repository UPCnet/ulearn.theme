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
        self.query = self.request.form.get('q', '')

    def get_my_communities(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()
        return pc.searchResults(portal_type="ulearn.community",
                                subscribed_users=current_user,
                                sort_on="sortable_title",)

    def get_batched_communities(self, query=None, batch=True, b_size=10, b_start=0):
        pc = getToolByName(self.context, "portal_catalog")
        results = pc.searchResults(portal_type="ulearn.community")
        batch = Batch(results, b_size, b_start)
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

    def get_communities_by_query(self):
        pc = getToolByName(self.context, "portal_catalog")

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'

            results = pc.searchResults(portal_type="ulearn.community", SearchableText=query)
            return results
        else:
            return ''


class communities(baseCommunities):
    """ The list of communities """
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.layer(IUlearnTheme)


class communitiesAJAX(baseCommunities):
    """ The list of communities via AJAX """
    grok.name('my-communities-ajax')
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.template('my_communities_ajax')
    grok.layer(IUlearnTheme)


class searchCommunitiesAJAX(baseCommunities):
    """ Search communities via AJAX """
    grok.name('search-communities-ajax')
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.template('search_communities_ajax')
    grok.layer(IUlearnTheme)
