from scss import Scss
from DateTime import DateTime
from zope.interface import alsoProvides

from five import grok
from plone import api
from zope.component.hooks import getSite
from Acquisition import aq_inner
from zope.interface import Interface
from zope.component import queryUtility
from zope.component import getUtilitiesFor
from zope.component import getUtility
from souper.interfaces import ICatalogFactory

from plone.memoize import ram
from plone.batching import Batch
from plone.memoize.view import memoize_contextless
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from plone.app.users.browser.personalpreferences import UserDataPanel

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot

from genweb.theme.browser.views import HomePageBase
from genweb.theme.browser.interfaces import IHomePageView
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.folder import FolderView
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
from genweb.core.utils import json_response

from souper.soup import get_soup
from repoze.catalog.query import Eq
from Products.statusmessages.interfaces import IStatusMessage

from zope.i18n import translate

order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}


class homePage(HomePageBase):
    """ Override the original homepage as it will be always restricted to auth users """
    grok.implements(IHomePageView)
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.layer(IUlearnTheme)


class baseCommunities(grok.View):
    grok.baseclass()

    def update(self):
        self.username = api.user.get_current().id
        self.portal_url = api.portal.get().absolute_url()

    @memoize_contextless
    def portal(self):
        return getSite()

    def get_all_communities(self):
        pc = api.portal.get_tool('portal_catalog')
        r_results = pc.searchResults(portal_type="ulearn.community", community_type=[u"Closed", u"Organizative"])
        ur_results = pc.unrestrictedSearchResults(portal_type="ulearn.community", community_type=u"Open")
        return r_results + ur_results

    def get_authenticator(self):
        return createToken()


class AllCommunities(baseCommunities):
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
            return '@import "{}/ulearncustom.css";\n'.format(api.portal.get().absolute_url()) + \
                   self.compile_scss(main_color=self.settings.main_color,
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
            return '@import "{}/ulearncustom.css";'.format(api.portal.get().absolute_url())

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


class CustomCSS(grok.View):
    grok.name('ulearncustom.css')
    grok.context(Interface)
    grok.layer(IUlearnTheme)

    index = ViewPageTemplateFile('views_templates/ulearncustom.css.pt')

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        return self.index()


class SearchUser(grok.View):
    grok.name('searchUser')
    grok.context(Interface)

    @json_response
    def render(self):
        return {'users': self.get_my_users(),
                'properties': self.get_user_info_for_display()}

    def get_my_users(self):
        searchby = ''
        if len(self.request.form) > 0:
            searchby = self.request.form['search']
        elif 'search' in self.request:
            searchby = self.request.get('search')
        resultat = searchUsersFunction(self.context, self.request, searchby)

        return resultat

    def get_user_info_for_display(self):
        user_properties_utility = getUtility(ICatalogFactory, name='user_properties')

        rendered_properties = []
        extender_name = api.portal.get_registry_record('genweb.controlpanel.core.IGenwebCoreControlPanelSettings.user_properties_extender')
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            for prop in extended_user_properties_utility.directory_properties:
                rendered_properties.append(dict(
                    name=prop,
                    icon=extended_user_properties_utility.directory_icons[prop]
                ))
            return rendered_properties
        else:
            # If it's not extended, then return the simple set of data we know
            # about the user using also the directory_properties field
            for prop in user_properties_utility.directory_properties:
                rendered_properties.append(dict(
                    name=prop,
                    icon=user_properties_utility.directory_icons[prop]
                ))
            return rendered_properties


class searchUsers(grok.View):
    grok.name('searchUsers')
    grok.context(Interface)
    grok.require('genweb.member')
    grok.template('search_users')
    grok.layer(IUlearnTheme)

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
                # We have to add here an element to the JSON in case there is too many elements.
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

        items_favorites = self.marca_favoritos(r_results)
        items_nofavorites = self.exclude_favoritos(r_results)

        items = self.ordenar_results(items_favorites, items_nofavorites)

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

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

            return items
        else:
            r_results = pc.searchResults(path=path,
                                         Subject={'query': self.tags, 'operator': 'and'},
                                         sort_on='sortable_title',
                                         sort_order='ascending')

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

            return items

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

            items_favorites = self.marca_favoritos(r_results)
            items_nofavorites = self.exclude_favoritos(r_results)

            items = self.ordenar_results(items_favorites, items_nofavorites)

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

        r_results_parent = catalog.searchResults(path={'query': path, 'depth': 1},
                                                 sort_on='sortable_title',
                                                 sort_order='ascending')

        items_favorites = self.favorites_items(path)
        items_nofavorites = self.exclude_favoritos(r_results_parent)

        items = self.ordenar_results(items_favorites, items_nofavorites)

        return items

    def ordenar_results(self, items_favorites, items_nofavorites):
        """ Ordena los resultados segun el tipo (portal_type)
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5})
            y devuelve el diccionario con los favoritos y no favoritos. """
        items_favorites_by_tipus = sorted(items_favorites, key=lambda item: item['tipus'])
        items_nofavorites_by_tipus = sorted(items_nofavorites, key=lambda item: item['tipus'])

        items = [dict(favorite=items_favorites_by_tipus,
                      nofavorite=items_nofavorites_by_tipus)]
        return items

    def marca_favoritos(self, r_results):
        """ De los resultados obtenidos devuelve una lista con los que son FAVORITOS y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        current_user = api.user.get_current().id
        favorite = []
        favorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in r_results if current_user in r.favoritedBy]

        return favorite

    def exclude_favoritos(self, r_results):
        """ De los resultados obtenidos devuelve una lista con los que NO son FAVORITOS y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        current_user = api.user.get_current().id
        nofavorite = []
        nofavorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in r_results if current_user not in r.favoritedBy]

        return nofavorite

    def favorites_items(self, path):
        """ Devuelve todos los favoritos del usuario y le asigna un valor al tipus
            segun este orden: (order_by_type = {"Folder": 1, "Document": 2, "File": 3, "Link": 4, "Image": 5}) """
        pc = api.portal.get_tool(name='portal_catalog')
        current_user = api.user.get_current().id
        results = pc.searchResults(path={'query': path},
                                   favoritedBy=current_user,
                                   sort_on='sortable_title',
                                   sort_order='ascending')

        favorite = [{'obj': r, 'tipus': order_by_type[r.portal_type] if r.portal_type in order_by_type else 6} for r in results]
        return favorite


class SearchFilteredContentAjax(FilteredContentsSearchView):
    """ Ajax helper for filtered content search view for every folder. """
    grok.name('search_filtered_content')
    grok.context(Interface)
    grok.template('filtered_contents_search_ajax')
    grok.layer(IUlearnTheme)


class SummaryViewNews(FolderView):

    def __init__(self, *args, **kwargs):
        super(SummaryViewNews, self).__init__(*args, **kwargs)
        context = aq_inner(self.context)
        self.collection_behavior = ICollection(context)
        self.b_size = self.collection_behavior.item_count

    def results(self, **kwargs):
        """Return a content listing based result set with results from the
        collection query.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        contentFilter = self.request.get('contentFilter', {})
        contentFilter.update(kwargs.get('contentFilter', {}))
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        # collection is already batched.
        return self.results()

    def getFoldersAndImages(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.getFoldersAndImages(**kwargs)

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.selectedViewFields()

    def abrevia(self, summary, sumlenght):
        """ Retalla contingut de cadenes
        """
        bb = ''

        if sumlenght < len(summary):
            bb = summary[:sumlenght]

            lastspace = bb.rfind(' ')
            cutter = lastspace
            precut = bb[0:cutter]

            if precut.count('<b>') > precut.count('</b>'):
                cutter = summary.find('</b>', lastspace) + 4
            elif precut.count('<strong>') > precut.count('</strong>'):
                cutter = summary.find('</strong>', lastspace) + 9
            bb = summary[0:cutter]

            if bb.count('<p') > precut.count('</p'):
                bb += '...</p>'
            else:
                bb = bb + '...'
        else:
            bb = summary

        return bb

    def effectiveDate(self, item):
        if item.EffectiveDate() == 'None':
            date = str(item.creation_date.day()) + '/' + str(item.creation_date.month()) + '/' + str(item.creation_date.year()),
        else:
            date = str(item.effective_date.day()) + '/' + str(item.effective_date.month()) + '/' + str(item.effective_date.year()),
        return date[0]

    def abreviaText(self, item):
        text = self.abrevia(item.text.raw, 180)
        return text


class AllTags(grok.View):
    grok.name('alltags')
    grok.context(Interface)
    grok.require('genweb.authenticated')
    grok.template('alltags')
    grok.layer(IUlearnTheme)

    def get_subscribed_tags(self):
        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id

        soup_tags = get_soup('user_subscribed_tags', portal)
        tags_soup = [r for r in soup_tags.query(Eq('id', userid))]

        return tags_soup[0].attrs['tags'] if tags_soup else []

    def get_unsubscribed_tags(self):

        subjects = []
        pc = api.portal.get_tool('portal_catalog')
        subjs_index = pc._catalog.indexes['Subject']
        [subjects.append(index[0]) for index in subjs_index.items()]

        portal = getSite()
        current_user = api.user.get_current()
        userid = current_user.id

        soup_tags = get_soup('user_subscribed_tags', portal)
        tags_soup = [r for r in soup_tags.query(Eq('id', userid))]
        if tags_soup:
            user_tags = tags_soup[0].attrs['tags']
        else:
            user_tags = ()
        return list(set(subjects) - set(user_tags))


class SearchFilteredNews(grok.View):
    """ Filtered news search view for every folder. """
    grok.name('search_filtered_news')
    grok.context(Interface)
    grok.layer(IUlearnTheme)

    def render(self):

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        def abrevia(summary, sumlenght):
            """ Retalla contingut de cadenes
            """
            bb = ''

            if sumlenght < len(summary):
                bb = summary[:sumlenght]

                lastspace = bb.rfind(' ')
                cutter = lastspace
                precut = bb[0:cutter]

                if precut.count('<b>') > precut.count('</b>'):
                    cutter = summary.find('</b>', lastspace) + 4
                elif precut.count('<strong>') > precut.count('</strong>'):
                    cutter = summary.find('</strong>', lastspace) + 9
                bb = summary[0:cutter]

                if bb.count('<p') > precut.count('</p'):
                    bb += '...</p>'
                else:
                    bb = bb + '...'
            else:
                bb = summary

            return bb

        def makeHtmlData(news_list):
            news_html = ''
            current = api.user.get_current()
            lang = current.getProperty('language')
            readmore = translate("readmore", "ulearn", None, None, lang, None)
            if news_list:
                for noticia in news_list:
                    noticiaObj = noticia.getObject()
                    if noticiaObj.text is None:
                        text = ''
                    else:
                        if noticiaObj.description:
                            text = abrevia(noticiaObj.description, 150)
                        else:
                            text = abrevia(noticiaObj.text.raw, 150)

                    news_html += '<li class="noticies clearfix">' \
                                   '<div>' \
                                      '<div class="imatge_noticia">' \
                                      '<img src="' + noticia.getURL() + '/@@images/image/thumb" alt="' + noticiaObj.id + '" title="' + noticiaObj.id + '" class="newsImage" width="222" height="222">'\
                                      '</div>' \
                                      '<div class="text_noticia">' \
                                        '<h2>'\
                                        '<a href="' + noticia.getURL() + '">' + abrevia(noticia.Title, 70) + '</a>'\
                                        '</h2>'\
                                        '<p><time class="smaller">' + str(noticiaObj.modification_date.day()) + '/' + str(noticiaObj.modification_date.month()) + '/' + str(noticiaObj.modification_date.year()) + '</time></p>'\
                                        '<span>' + text.encode('utf-8') + '</span>'\
                                        '<a href="' + noticia.getURL() + '" class="readmore" title="' + abrevia(noticia.Title, 70) + '"><span class="readmore">' + readmore.encode('utf-8') + '</span>'\
                                        '</a>'\
                                      '</div>'\
                                   '</div>'\
                                 '</li>'
            else:
                news_html = '<li class="noticies clearfix"><div> No hay coincidencias. </div></li>'
            return news_html

        pc = getToolByName(self.context, "portal_catalog")
        now = DateTime()
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        self.query = self.request.form.get('q', '')
        if not self.query == '':
            multispace = u'\u3000'.encode('utf-8')
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'
            r_results = pc.searchResults(portal_type='News Item',
                                         review_state='intranet',
                                         expires={'query': now, 'range': 'min', },
                                         sort_on='created',
                                         sort_order='reverse',
                                         is_outoflist=False,
                                         SearchableText=query
                                         )

            data = makeHtmlData(r_results)
            return data

        else:
            r_results = pc.searchResults(portal_type='News Item',
                                         review_state='intranet',
                                         expires={'query': now, 'range': 'min', },
                                         sort_on='created',
                                         sort_order='reverse',
                                         is_outoflist=False
                                         )

            data = makeHtmlData(r_results)
            return data


class ContentsPrettyView(grok.View):
    """ Show content in a pretty way for every folder. """
    grok.name('contents_pretty_view')
    grok.context(Interface)
    grok.require('genweb.member')
    grok.template('contents_pretty')
    grok.layer(IUlearnTheme)

    def getItemPropierties(self):
        all_items = []

        portal = api.portal.get()
        catalog = getToolByName(portal, 'portal_catalog')
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        nElements = 2
        llistaElements = []

        items = catalog.searchResults(path={'query': path, 'depth': 1},
                                      sort_on="getObjPositionInParent")
        all_items += [{'item_title': item.Title,
                       'item_desc': item.Description[:110],
                       'item_type': item.portal_type,
                       'item_url': item.getURL(),
                       'item_path': item.getPath(),
                       'item_state': item.review_state,
                       } for item in items if item.exclude_from_nav is False]

        if len(all_items) > 0:
            # Retorna una llista amb els elements en blocs de 2 elements
            llistaElements = [all_items[i:i + nElements] for i in range(0, len(all_items), nElements)]
        return llistaElements

    def getBlocs(self):
        llistaElements = self.getItemPropierties()
        return len(llistaElements)

    def getSubItemPropierties(self, item_path):
        all_items = []
        portal = api.portal.get()
        catalog = getToolByName(portal, 'portal_catalog')
        path = item_path

        items = catalog.searchResults(path={'query': path, 'depth': 1},
                                      sort_on="getObjPositionInParent")
        all_items += [{'item_title': item2.Title,
                       'item_desc': item2.Description[:120],
                       'item_type': item2.portal_type,
                       'item_url': item2.getURL(),
                       'item_state': item2.review_state
                       } for item2 in items if item2.exclude_from_nav is False]
        return all_items


class SharedWithMe(baseCommunities):
    """ The list of communities """
    grok.context(IPloneSiteRoot)
    grok.require('genweb.member')
    grok.layer(IUlearnTheme)


class resetMenuBar(grok.View):
    """ This view resets the links menu. And refresh them when accesing to personal_bar...always :) """
    grok.name('reset_menu')
    grok.context(IPloneSiteRoot)
    grok.layer(IUlearnTheme)

    def render(self):
        """ clear the soup from links... recreated rendering the personal_bar.pt"""
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        soup_menu = get_soup('menu_soup', portal)
        soup_menu.clear()
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        from ulearn.core import _
        IStatusMessage(self.request).addStatusMessage(_(u"menu-reset-menu-msg"), type='success')
        return self.request.response.redirect(self.context.absolute_url())
