from five import grok
from zope.component.hooks import getSite

from plone.batching import Batch
from plone.memoize.view import memoize_contextless
from plone.protect import createToken

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

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def get_authenticator(self):
        return createToken()

    def get_my_communities(self):
        pm = getToolByName(self.portal(), "portal_membership")
        pc = getToolByName(self.portal(), "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()
        return pc.searchResults(portal_type="ulearn.community",
                                subscribed_users=current_user)
                                #sort_on="sortable_title",)

    def get_batched_communities(self, query=None, batch=True, b_size=10, b_start=0):
        pc = getToolByName(self.context, "portal_catalog")
        r_results = pc.searchResults(portal_type="ulearn.community", community_type=[u"Closed", u"Organizative"])
        ur_results = pc.unrestrictedSearchResults(portal_type="ulearn.community", community_type=u"Open")
        batch = Batch(r_results + ur_results, b_size, b_start)
        return batch

    def is_community_manager(self, community):
        pm = getToolByName(self.context, "portal_membership")
        user = pm.getAuthenticatedMember()
        current_user = user.getUserName()

        return 'Manager' in user.getRoles() or \
               'WebMaster' in user.getRoles() or \
               'Site Administrator' in user.getRoles() or \
               'Owner' in community.get_local_roles_for_userid(user.id) or \
               current_user == community.Creator

    def get_favorites(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()

        results = pc.unrestrictedSearchResults(favoritedBy=current_user)
        return [favorites.id for favorites in results]

    def is_not_organizative(self, community):
        return not community.community_type == u'Organizative'

    def get_star_class(self, community):
        return community.id in self.favorites and 'fa-icon-star' or 'fa-icon-star-empty'

    def get_subscribed_class(self, community):
        pm = getToolByName(self.context, "portal_membership")
        user = pm.getAuthenticatedMember()
        current_user = user.getUserName()
        if community.community_type == u'Organizative':
            return ''
        else:
            # It's an open community or a closed one where I'm subscribed. If
            # the community is closed and I'm not subscribed, then I should not
            # see it as I should not have permission
            return 'fa-icon-check' if current_user in community.subscribed_users else 'fa-icon-check-empty'

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

            r_results = pc.searchResults(portal_type="ulearn.community",
                                       community_type=[u"Closed", u"Organizative"],
                                       SearchableText=query)
            ur_results = pc.unrestrictedSearchResults(portal_type="ulearn.community",
                                                      community_type=u"Open",
                                                      SearchableText=query)
            return r_results + ur_results
        else:
            return self.get_batched_communities(query=None, batch=True, b_size=10, b_start=0)


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
