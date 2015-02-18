from scss import Scss
from DateTime import DateTime

from five import grok
from plone import api
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
from ulearn.core.browser.searchuser import searchUsersFunction
from ulearn.core.interfaces import IDiscussionFolder

from Products.PythonScripts.standard import url_quote_plus
from Products.CMFPlone.browser.navtree import getNavigationRoot
from genweb.core.utils import pref_lang
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
import json
import scss
import pkg_resources


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
        self.portal_url = api.portal.get().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def get_authenticator(self):
        return createToken()

    def get_my_communities(self):
        pm = api.portal.get_tool('portal_membership')
        pc = api.portal.get_tool('portal_catalog')
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
        roles = api.user.get_roles(obj=community.getObject())

        return 'Manager' in roles or \
               'Site Administrator' in roles or \
               'Owner' in roles

    def get_favorites(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()

        results = pc.unrestrictedSearchResults(favoritedBy=current_user)
        return [favorites.id for favorites in results]

    def is_not_organizative(self, community):
        return not community.community_type == u'Organizative'

    def get_star_class(self, community):
        return community.id in self.favorites and 'fa fa-star' or 'fa fa-star-o'

    def authenticated_user_is_subscribed(self, community):
        pm = getToolByName(self.context, "portal_membership")
        user = pm.getAuthenticatedMember()
        current_user = user.getUserName()
        return current_user in community.subscribed_users

    def favorite_button_enabled(self, community):
        return self.authenticated_user_is_subscribed(community)

    def get_subscribed_class(self, community):
        if community.community_type == u'Organizative':
            return ''
        else:
            # It's an open community or a closed one where I'm subscribed. If
            # the community is closed and I'm not subscribed, then I should not
            # see it as I should not have permission
            return 'fa fa-check-square-o' if self.authenticated_user_is_subscribed(community) else 'fa fa-square-o'

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
                     alt_gradient_start_color, alt_gradient_end_color, color_community_closed, color_community_organizative, color_community_open):
    """Cache by the specific colors"""
    return (main_color, secondary_color, background_property, background_color,
            buttons_color_primary, buttons_color_secondary, maxui_form_bg,
            alt_gradient_start_color, alt_gradient_end_color,
            color_community_closed, color_community_organizative, color_community_open)


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
           self.settings.alt_gradient_end_color and \
           self.settings.color_community_closed and \
           self.settings.color_community_organizative and \
           self.settings.color_community_open:
            return self.compile_scss(main_color=self.settings.main_color,
                                     secondary_color=self.settings.secondary_color,
                                     background_property=self.settings.background_property,
                                     background_color=self.settings.background_color,
                                     buttons_color_primary=self.settings.buttons_color_primary,
                                     buttons_color_secondary=self.settings.buttons_color_secondary,
                                     maxui_form_bg=self.settings.maxui_form_bg,
                                     alt_gradient_start_color=self.settings.alt_gradient_start_color,
                                     alt_gradient_end_color=self.settings.alt_gradient_end_color,
                                     color_community_closed=self.settings.color_community_closed,
                                     color_community_organizative=self.settings.color_community_organizative,
                                     color_community_open=self.settings.color_community_open)

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
                        alt_gradient_end_color=self.settings.alt_gradient_end_color,
                        color_community_closed=self.settings.color_community_closed,
                        color_community_organizative=self.settings.color_community_organizative,
                        color_community_open=self.settings.color_community_open)

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
        $color_community_closed: {color_community_closed};
        $color_community_organizative: {color_community_organizative};
        $color_community_open: {color_community_open};

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


class SearchUser(grok.View):
    grok.name('searchUser')
    grok.context(Interface)
    grok.template('search_users_ajax')

    def get_my_users(self):
        if 'search' in self.request:
            searchString = self.request.get('search')
        else:
            searchString = ''

        resultat = searchUsersFunction(self.context, self.request, searchString)
        return resultat


class searchUsers(grok.View):
    grok.name('searchUsers')
    grok.context(Interface)
    grok.require('genweb.member')
    grok.template('search_users')
    grok.layer(IUlearnTheme)

    def users(self):
        searchby = ''
        if len(self.request.form) > 0:
            searchby = self.request.form['search']

        resultat = searchUsersFunction(self.context, self.request, searchby)
        return resultat

    def get_people_literal(self):
        return api.portal.get_registry_record(name='ulearn.core.controlpanel.IUlearnControlPanelSettings.people_literal')


class showOportunitats(grok.View):
    grok.name('showOportunitats')
    grok.context(Interface)
    grok.template('show_oportunitats')

    def get_states(self):
        pw = getToolByName(self.context, 'portal_workflow')
        ordered_states = ['Idea', 'Oportunitat', 'Disseny de concepte', 'Pla de marqueting', 'Solucio tecnologica i promocio', 'Transferencia de coneixement', 'Mercat', 'Arxivada', 'Realitzada', 'Rebutjada']
        resultat = []
        for state in ordered_states:
            resultat.append([state, pw['oportunity'].states[state].title])
        return resultat

    def get_oportunitats(self):
        pc = getToolByName(self.context, 'portal_catalog')
        oportunitats = pc.searchResults(portal_type='ulearn.oportunity')
        resultat = {}

        for oportunitat in oportunitats:
            if oportunitat.review_state not in resultat.keys():
                resultat[oportunitat.review_state] = [oportunitat]
            else:
                resultat[oportunitat.review_state].append(oportunitat)
        return resultat


class ULearnPersonalPreferences(UserDataPanel):
    """
        Override original personal preferences to disable right column portlet
    """

    def __init__(self, context, request):
        super(ULearnPersonalPreferences, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', True)


class DiscussionFolderView(grok.View):
    grok.name('discussion_folder_view')
    grok.context(IDiscussionFolder)
    grok.template('discussion_folder_view')
    grok.layer(IUlearnTheme)

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def get_folder_discussions(self):
        pc = api.portal.get_tool(name="portal_catalog")
        path = "/".join(self.context.getPhysicalPath())
        results = pc.searchResults(portal_type="ulearn.discussion",
                                   path={'query': path},
                                   sort_on='created')
        return results

    def get_last_comment_from_discussion(self, discussion):
        pc = api.portal.get_tool(name="portal_catalog")
        pm = api.portal.get_tool(name="portal_membership")
        results = pc.searchResults(portal_type="Discussion Item",
                                   path={'query': discussion.getPath()},
                                   sort_on='created',
                                   sort_order='reverse')
        if results:
            comment = results[0].getObject()

            return dict(text=comment.getText(),
                        author_username=comment.author_username,
                        author_name=comment.author_name,
                        portrait_url=pm.getPersonalPortrait(comment.author_username).absolute_url(),
                        modification_date=comment.modification_date)
        else:
            return None

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.isoformat())
        return util.toLocalizedTime(zope_time, long_format=True)


class TypeAheadSearch(grok.View):
    grok.name('gw_type_ahead_search')
    grok.context(Interface)
    grok.layer(IUlearnTheme)

    def render(self):
        # We set the parameters sent in livesearch using the old way.
        q = self.request['q']
        cf = self.request['cf']
        limit = 10
        path = None
        if cf != '':
            path = cf
        ploneUtils = getToolByName(self.context, 'plone_utils')
        portal_url = getToolByName(self.context, 'portal_url')()
        pretty_title_or_id = ploneUtils.pretty_title_or_id
        portalProperties = getToolByName(self.context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        # SIMPLE CONFIGURATION
        MAX_TITLE = 40
        MAX_DESCRIPTION = 80

        # generate a result set for the query
        catalog = self.context.portal_catalog

        friendly_types = ploneUtils.getUserFriendlyTypes()

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_bad_chars(r) + '*'
        searchterms = url_quote_plus(r)

        params = {'SearchableText': r,
                  'portal_type': friendly_types,
                  'sort_limit': limit + 1}

        if path is None:
            # useful for subsides
            params['path'] = getNavigationRoot(self.context)
        else:
            params['path'] = path

        params["Language"] = pref_lang()
        # search limit+1 results to know if limit is exceeded
        results = catalog(**params)

        REQUEST = self.context.REQUEST
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', 'application/json')

        label_show_all = _('label_show_all', default='Show all items')

        ts = getToolByName(self.context, 'translation_service')

        queryElements = []

        if results:
            # TODO: We have to build a JSON with the desired parameters.
            for result in results[:limit]:
                # Calculate icon replacing '.' per '-' as '.' in portal_types break CSS
                icon = result.portal_type.lower().replace(".", "-")
                itemUrl = result.getURL()
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                full_title = safe_unicode(pretty_title_or_id(result))
                if len(full_title) > MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE], '...'))
                else:
                    display_title = full_title

                full_title = full_title.replace('"', '&quot;')

                display_description = safe_unicode(result.Description)
                if len(display_description) > MAX_DESCRIPTION:
                    display_description = ''.join(
                        (display_description[:MAX_DESCRIPTION], '...'))

                # We build the dictionary element with the desired parameters and we add it to the queryElements array.
                queryElement = {'class': '', 'title': display_title, 'description': display_description, 'itemUrl': itemUrl, 'icon': icon}
                queryElements.append(queryElement)

            if len(results) > limit:
                #We have to add here an element to the JSON in case there is too many elements.
                searchquery = '/@@search?SearchableText=%s&path=%s' \
                    % (searchterms, params['path'])
                too_many_results = {'class': 'with-separator', 'title': ts.translate(label_show_all, context=REQUEST), 'description': '', 'itemUrl': portal_url + searchquery, 'icon': ''}
                queryElements.append(too_many_results)

        return json.dumps(queryElements)


class FilteredContentsSearchView(grok.View):
    """ Filtered content search view for every folder. """
    grok.name('filtered_contents_search_view')
    grok.context(Interface)
    grok.require('genweb.member')
    grok.template('filtered_contents_search')
    grok.layer(IUlearnTheme)

    def update(self):
        self.query = self.request.form.get('q', '')
        if self.request.form.get('t', ''):
            self.tags = [v for v in self.request.form.get('t').split(',')]
        else:
            self.tags = []

    def get_batched_contenttags(self, query=None, batch=True, b_size=10, b_start=0):
        pc = getToolByName(self.context, "portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        r_results = pc.searchResults(path=path,
                                     sort_on='sortable_title',
                                     sort_order='ascending')
        items = self.marca_favoritos(r_results)
        batch = Batch(items, b_size, b_start)
        return batch

    def get_contenttags_by_query(self):
        pc = getToolByName(self.context, "portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query and not self.tags:
            return self.getContent()

        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'

            if self.tags:
                r_results = pc.searchResults(path=path,
                                             SearchableText=query,
                                             Subject={'query': self.tags, 'operator': 'and'},
                                             sort_on='sortable_title',
                                             sort_order='ascending')
            else:
                r_results = pc.searchResults(path=path,
                                             SearchableText=query,
                                             sort_on='sortable_title',
                                             sort_order='ascending')

            items = self.marca_favoritos(r_results)
            return items
        else:
            r_results = pc.searchResults(path=path,
                                         Subject={'query': self.tags, 'operator': 'and'},
                                         sort_on='sortable_title',
                                         sort_order='ascending')

            items = self.marca_favoritos(r_results)
            return items
            # return self.get_batched_contenttags(query=None, batch=True, b_size=10, b_start=0)

    def get_tags_by_query(self):
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
            query = quote_bad_chars(query)
            path = self.context.absolute_url_path()

            r_results = pc.searchResults(path=path,
                                         Subject=query,
                                         sort_on='sortable_title',
                                         sort_order='ascending')

            items = self.marca_favoritos(r_results)
            return items
        else:
            return self.get_batched_contenttags(query=None, batch=True, b_size=10, b_start=0)

    def get_container_path(self):
        return self.context.absolute_url()

    def getContent(self):
        portal = api.portal.get()
        catalog = getToolByName(portal, 'portal_catalog')
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        r_results_all = catalog.searchResults(path={'query': path},
                              sort_on='sortable_title',
                              sort_order='ascending')

        r_results_parent = catalog.searchResults(path={'query': path, 'depth': 1},
                                      sort_on='sortable_title',
                                      sort_order='ascending')

        items_favorites = self.get_list_favorites(r_results_all)
        items_nofavorites = self.get_list_nofavorites(r_results_parent)
        items = [dict(favorite=items_favorites,
                      nofavorite=items_nofavorites)]
        return items

    def get_list_favorites(self,r_results):
        pc = getToolByName(self.context, "portal_catalog")
        favorites_list = self.favorites_items()
        favorite = []
        favorite_folder = []

        for item in r_results:
            if item.id in favorites_list:
                if item.portal_type == 'Folder':
                    favorite_folder.append(item)
                else:
                    favorite.append(item)
        items = favorite_folder + favorite
        return items

    def get_list_nofavorites(self, r_results):
        pc = getToolByName(self.context, "portal_catalog")
        favorites_list = self.favorites_items()
        nofavorite = []
        nofavorite_folder = []

        for item in r_results:
            if item.id not in favorites_list:
                if item.portal_type == 'Folder':
                    nofavorite_folder.append(item)
                else:
                    nofavorite.append(item)
        items = nofavorite_folder + nofavorite
        return items

    def marca_favoritos(self, r_results):
        pc = getToolByName(self.context, "portal_catalog")
        favorites_list = self.favorites_items()
        favorite = []
        nofavorite = []
        favorite_folder = []
        nofavorite_folder = []

        for item in r_results:
            if item.id in favorites_list:
                if item.portal_type == 'Folder':
                    favorite_folder.append(item)
                else:
                    favorite.append(item)
            else:
                if item.portal_type == 'Folder':
                    nofavorite_folder.append(item)
                else:
                    nofavorite.append(item)
        items = [dict(favorite=favorite_folder + favorite,
                      nofavorite=nofavorite_folder + nofavorite)]
        return items      

    def favorites_items(self):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()
        results = pc.unrestrictedSearchResults(favoritedBy=current_user)
        self.favorites = [favorites.id for favorites in results]
        return self.favorites

    def item_is_favorite(self,contingut):
        pm = getToolByName(self.context, "portal_membership")
        pc = getToolByName(self.context, "portal_catalog")
        current_user = pm.getAuthenticatedMember().getUserName()

        results = pc.unrestrictedSearchResults(favoritedBy=current_user)

        self.favorites = [favorites.id for favorites in results]
        return contingut.id in self.favorites


class SearchFilteredContentAjax(FilteredContentsSearchView):
    """ Ajax helper for filtered content search view for every folder. """
    grok.name('search_filtered_content')
    grok.context(Interface)
    grok.template('filtered_contents_search_ajax')
    grok.layer(IUlearnTheme)

