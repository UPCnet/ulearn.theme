from scss import Scss

from five import grok
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.component import queryUtility

from plone.memoize import ram
from plone.batching import Batch
from plone.memoize.view import memoize_contextless
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from plone.app.users.browser.personalpreferences import UserDataPanel

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from genweb.theme.browser.views import HomePageBase
from genweb.theme.browser.interfaces import IHomePageView

from ulearn.theme.browser.interfaces import IUlearnTheme
from ulearn.core.controlpanel import IUlearnControlPanelSettings

import pkg_resources
import scss


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


def _render_cachekey(method, self, main_color, secondary_color, background_property, background_color,
                     buttons_color_primary, buttons_color_secondary, maxui_form_bg,
                     alt_gradient_start_color, alt_gradient_end_color):
    """Cache by the specific colors"""
    return (main_color, secondary_color, background_property, background_color,
            buttons_color_primary, buttons_color_secondary, maxui_form_bg,
            alt_gradient_start_color, alt_gradient_end_color)


class dynamicCSS(grok.View):
    grok.name('dynamic.css')
    grok.context(Interface)
    grok.layer(IUlearnTheme)

    def update(self):
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IUlearnControlPanelSettings)

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        self.request.response.addHeader('Cache-Control', 'must-revalidate, max-age=0, no-cache, no-store')
        if self.settings.main_color and self.settings.secondary_color and \
           self.settings.background_property and \
           self.settings.background_color and \
           self.settings.buttons_color_primary and \
           self.settings.buttons_color_secondary and \
           self.settings.maxui_form_bg and \
           self.settings.alt_gradient_start_color and \
           self.settings.alt_gradient_end_color:
            return self.compile_scss(main_color=self.settings.main_color,
                                     secondary_color=self.settings.secondary_color,
                                     background_property=self.settings.background_property,
                                     background_color=self.settings.background_color,
                                     buttons_color_primary=self.settings.buttons_color_primary,
                                     buttons_color_secondary=self.settings.buttons_color_secondary,
                                     maxui_form_bg=self.settings.maxui_form_bg,
                                     alt_gradient_start_color=self.settings.alt_gradient_start_color,
                                     alt_gradient_end_color=self.settings.alt_gradient_end_color)
        else:
            return ""

    @ram.cache(_render_cachekey)
    def compile_scss(self, **kwargs):
        genwebthemeegg = pkg_resources.get_distribution('genweb.theme')
        ulearnthemeegg = pkg_resources.get_distribution('ulearn.theme')
        scssfile = open('{}/ulearn/theme/scss/dynamic.scss'.format(ulearnthemeegg.location))

        settings = dict(main_color=self.settings.main_color,
                        secondary_color=self.settings.secondary_color,
                        background_property=self.settings.background_property,
                        background_color=self.settings.background_color,
                        buttons_color_primary=self.settings.buttons_color_primary,
                        buttons_color_secondary=self.settings.buttons_color_secondary,
                        maxui_form_bg=self.settings.maxui_form_bg,
                        alt_gradient_start_color=self.settings.alt_gradient_start_color,
                        alt_gradient_end_color=self.settings.alt_gradient_end_color)

        variables_scss = """

        $main-color: {main_color};
        $secondary-color: {secondary_color};
        $background-property: {background_property};
        $background-color: {background_color};
        $buttons-color-primary: {buttons_color_primary};
        $buttons-color-secondary: {buttons_color_secondary};
        $maxui-form-bg: {maxui_form_bg};
        $alt-gradient-start-color: {alt_gradient_start_color};
        $alt-gradient-end-color: {alt_gradient_end_color};

        """.format(**settings)

        scss.config.LOAD_PATHS = [
            '{}/genweb/theme/bootstrap/scss/compass_twitter_bootstrap'.format(genwebthemeegg.location)
        ]

        css = Scss(scss_opts={
                   'compress': False,
                   'debug_info': False,
                   })

        dynamic_scss = ''.join([variables_scss, scssfile.read()])

        return css.compile(dynamic_scss)


class ULearnPersonalPreferences(UserDataPanel):
    """
        Override original personal preferences to disable right column portlet
    """

    def __init__(self, context, request):
        super(ULearnPersonalPreferences, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', True)
