# -*- coding: utf-8 -*-
from zope import schema
from z3c.form import button
from zope.component import getUtility, getMultiAdapter
from zope.component.hooks import getSite

from plone.portlets.utils import registerPortletType, unregisterPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel

from mrs.max import MRSMAXMessageFactory as _

from plone.directives import form


class IPortletsSettings(form.Schema):
    """Enable allowed portlets on plone site.
    """

    # ==== Portlets ====

    genweb_portlets_news_events_listing = schema.Bool(
        title=_(u'genweb_portlets_news_events_listing',
                default=_(u"Habilitar portlet genweb_portlets_news_events_listing")),
        description=_(u'help_genweb_portlets_news_events_listing',
                      default=_(u"Habilita el portlet genweb_portlets_news_events_listing.")),
        required=False,
        default=False,
    )

    portlets_Search = schema.Bool(
        title=_(u'portlets_Search',
                default=_(u"Habilitar portlet portlets_Search")),
        description=_(u'help_portlets_Search',
                      default=_(u"Habilita el portlet portlets_Search.")),
        required=False,
        default=False,
    )

    portlets_Review = schema.Bool(
        title=_(u'portlets_Review',
                default=_(u"Habilitar portlet portlets_Review")),
        description=_(u'help_portlets_Review',
                      default=_(u"Habilita el portlet portlets_Review.")),
        required=False,
        default=False,
    )

    portlets_Recent = schema.Bool(
        title=_(u'portlets_Recent',
                default=_(u"Habilitar portlet portlets_Recent")),
        description=_(u'help_portlets_Recent',
                      default=_(u"Habilita el portlet portlets_Recent.")),
        required=False,
        default=False,
    )

    portlets_News = schema.Bool(
        title=_(u'portlets_News',
                default=_(u"Habilitar portlet portlets_News")),
        description=_(u'help_portlets_News',
                      default=_(u"Habilita el portlet portlets_News.")),
        required=False,
        default=False,
    )

    mrs_max_widget = schema.Bool(
        title=_(u'mrs_max_widget',
                default=_(u"Habilitar portlet mrs_max_widget")),
        description=_(u'help_mrs_max_widget',
                      default=_(u"Habilita el portlet mrs_max_widget.")),
        required=False,
        default=False,
    )

    portlets_Events = schema.Bool(
        title=_(u'portlets_Events',
                default=_(u"Habilitar portlet portlets_Events")),
        description=_(u'help_portlets_Events',
                      default=_(u"Habilita el portlet portlets_Events.")),
        required=False,
        default=False,
    )

    portlets_Calendar = schema.Bool(
        title=_(u'portlets_Calendar',
                default=_(u"Habilitar portlet portlets_Calendar")),
        description=_(u'help_portlets_Calendar',
                      default=_(u"Habilita el portlet portlets_Calendar.")),
        required=False,
        default=False,
    )

    plone_portlet_collection_Collection = schema.Bool(
        title=_(u'plone_portlet_collection_Collection',
                default=_(u"Habilitar portlet plone_portlet_collection_Collection")),
        description=_(u'help_plone_portlet_collection_Collection',
                      default=_(u"Habilita el portlet plone_portlet_collection_Collection.")),
        required=False,
        default=False,
    )

    portlets_Login = schema.Bool(
        title=_(u'portlets_Login',
                default=_(u"Habilitar portlet portlets_Login")),
        description=_(u'help_portlets_Login',
                      default=_(u"Habilita el portlet portlets_Login.")),
        required=False,
        default=False,
    )

    portlets_Navigation = schema.Bool(
        title=_(u'portlets_Navigation',
                default=_(u"Habilitar portlet portlets_Navigation")),
        description=_(u'help_portlets_Navigation',
                      default=_(u"Habilita el portlet portlets_Navigation.")),
        required=False,
        default=False,
    )

    portlets_rss = schema.Bool(
        title=_(u'portlets_rss',
                default=_(u"Habilitar portlet portlets_rss")),
        description=_(u'help_portlets_rss',
                      default=_(u"Habilita el portlet portlets_rss.")),
        required=False,
        default=False,
    )

    plone_portlet_static_Static = schema.Bool(
        title=_(u'plone_portlet_static_Static',
                default=_(u"Habilitar portlet plone_portlet_static_Static")),
        description=_(u'help_plone_portlet_static_Static',
                      default=_(u"Habilita el portlet plone_portlet_static_Static.")),
        required=False,
        default=False,
    )

    collective_polls_VotePortlet = schema.Bool(
        title=_(u'collective_polls_VotePortlet',
                default=_(u"Habilitar portlet collective_polls_VotePortlet")),
        description=_(u'help_collective_polls_VotePortlet',
                      default=_(u"Habilita el portlet collective_polls_VotePortlet.")),
        required=False,
        default=False,
    )

    genweb_portlets_homepage = schema.Bool(
        title=_(u'portlet_homepage_title',
                default=_(u"Habilitar portlet homepage")),
        description=_(u'help_genweb_portlets_homepage',
                      default=_(u"Habilita el portlet homepage.")),
        required=False,
        default=False,
    )

    genweb_portlets_esdeveniments = schema.Bool(
        title=_(u'AgendaGW',
                default=_(u"Habilitar portlet esdeveniments")),
        description=_(u'help_genweb_portlets_esdeveniments',
                      default=_(u"Habilita el portlet esdeveniments.")),
        required=False,
        default=False,
    )

    genweb_portlets_news = schema.Bool(
        title=_(u'NoticiesPropi',
                default=_(u"Habilitar portlet News")),
        description=_(u'help_genweb_portlets_news',
                      default=_(u"Habilita el portlet News.")),
        required=False,
        default=False,
    )

    genweb_portlets_fullnews = schema.Bool(
        title=_(u'FullNews',
                default=_(u"Habilitar portlet Full News")),
        description=_(u'help_genweb_portlets_fullnews',
                      default=_(u"Habilita el portlet Full News.")),
        required=False,
        default=False,
    )

    genweb_portlets_upcnews = schema.Bool(
        title=_(u'UPCNews',
                default=_(u"Habilitar portlet Upc News")),
        description=_(u'help_genweb_portlets_upcnews',
                      default=_(u"Habilita el portlet Upc News.")),
        required=False,
        default=False,
    )

    ulearn_portlets_mytags = schema.Bool(
        title=_(u'ulearn_portlets_mytags',
                default=_(u"Habilitar portlet ulearn_portlets_mytags")),
        description=_(u'help_ulearn_portlets_mytags',
                      default=_(u"Habilita portlet amb el núvol de tags.")),
        required=False,
        default=False,
    )

    ulearn_portlets_mycommunities = schema.Bool(
        title=_(u'ulearn_portlets_mycommunities',
                default=_(u"Habilitar portlet ulearn_portlets_mycommunities")),
        description=_(u'help_ulearn_portlets_mycommunities',
                      default=_(u"Habilita el portlet que mostra les comunitats on estic suscrit o puc suscriurem.")),
        required=False,
        default=False,
    )

    ulearn_portlets_custombuttonbar = schema.Bool(
        title=_(u'ulearn_portlets_custombuttonbar',
                default=_(u"Habilitar portlet ulearn_portlets_custombuttonbar")),
        description=_(u'help_ulearn_portlets_custombuttonbar',
                      default=_(u"Habilita el portlet per a poder customitzar la botonera.")),
        required=False,
        default=False,
    )

    ulearn_portlets_subscribednews = schema.Bool(
        title=_(u'ulearn_portlets_subscribednews',
                default=_(u"Habilitar portlet ulearn_portlets_subscribednews")),
        description=_(u'help_ulearn_portlets_subscribednews',
                      default=_(u"Habilita el portlet per a veure les notícies les quals contenen un tag que segueixo.")),
        required=False,
        default=False,
    )

    ulearn_portlets_mysubjects = schema.Bool(
        title=_(u'ulearn_portlets_mysubjects',
                default=_(u"Habilitar portlet ulearn_portlets_mysubjects")),
        description=_(u'help_ulearn_portlets_mysubjects',
                      default=_(u"Habilita el portlet per a poder veure els meus cursos del EVA.")),
        required=False,
        default=False,
    )

    ulearn_portlets_angularrouteview = schema.Bool(
        title=_(u'ulearn_angularRouteView',
                default=_(u"Habilitar portlet angularRouteView")),
        description=_(u'help_ulearn_angularRouteView',
                      default=_(u"Habilita el portlet angular per a poder fer ús de les rutes angularjs.")),
        required=False,
        default=True,
    )

    ulearn_portlets_flashesinformativos = schema.Bool(
        title=_(u'ulearn_portlets_flashesinformativos',
                default=_(u"Habilitar portlet flashesinformativos")),
        description=_(u'help_ulearn_portlets_flashesinformativos',
                      default=_(u"Habilita el portlet para mostrar las notícias en el flash informativo.")),
        required=False,
        default=False,
    )

    ulearn_portlets_importantnews = schema.Bool(
        title=_(u'ulearn_portlets_importantnews',
                default=_(u"Habilitar portlet importantnews")),
        description=_(u'help_ulearn_portlets_importantnews',
                      default=_(u"Habilita el portlet para mostrar las notícias marcadas como destacadas.")),
        required=False,
        default=False,
    )

    ulearn_portlets_rss = schema.Bool(
        title=_(u'ulearn_portlets_rss',
                default=_(u"Habilitar portlet rss")),
        description=_(u'help_ulearn_portlets_rss',
                      default=_(u"Habilita el portlet per a mostrar contingut a partir d'un enllaç rss.")),
        required=False,
        default=False,
    )

    ulearn_portlets_buttonbar = schema.Bool(
        title=_(u'ulearn_button_bar',
                default=_(u"Habilitar portlet Ulearn Button Bar")),
        description=_(u'help_ulearn_button_bar',
                      default=_(u"Habilita el portlet botonera central.")),
        required=False,
        default=True,
    )

    ulearn_portlets_buttonbarangular = schema.Bool(
        title=_(u'ulearn_button_bar_angular',
                default=_(u"Habilitar portlet Ulearn Button Bar Angular")),
        description=_(u'help_ulearn_button_bar_angular',
                      default=_(u"Habilita el portlet botonera central configurable Angular.")),
        required=False,
        default=True,
    )

    ulearn_portlets_communities = schema.Bool(
        title=_(u'ulearn_communities',
                default=_(u"Habilitar portlet Ulearn Comunnities")),
        description=_(u'help_ulearn_communities',
                      default=_(u"Habilita el portlet lateral on mostra les comunitats favorites.")),
        required=False,
        default=True,
    )

    ulearn_portlets_profile = schema.Bool(
        title=_(u'ulearn_profile',
                default=_(u"Habilitar portlet Ulearn Profile")),
        description=_(u'help_ulearn_profile',
                      default=_(u"Habilita el portlet on mostra el perfil usuari, o la comunitat on estem.")),
        required=False,
        default=True,
    )

    ulearn_portlets_thinnkers = schema.Bool(
        title=_(u'ulearn_thinkers',
                default=_(u"Habilitar portlet Ulearn Thinkers")),
        description=_(u'help_ulearn_thinkers',
                      default=_(u"Habilita el portlet on es mostren els usuaris, amb la cerca .")),
        required=False,
        default=True,
    )

    ulearn_portlets_calendar = schema.Bool(
        title=_(u'ulearn_calendar',
                default=_(u"Habilitar portlet ulearn Calendar")),
        description=_(u'help_ulearn_calendar',
                      default=_(u"Habilita el portlet per a mostrar el calendari amb els events.")),
        required=False,
        default=True,
    )

    ulearn_portlets_discussion = schema.Bool(
        title=_(u'ulearn_discussion',
                default=_(u"Habilitar portlet Ulearn Discussion")),
        description=_(u'help_ulearn_discussion',
                      default=_(u"Habilita el portlet.")),
        required=False,
        default=False,
    )

    ulearn_portlets_econnect = schema.Bool(
        title=_(u'ulearn_econnect',
                default=_(u"Habilitar portlet Ulearn eConnect")),
        description=_(u'help_ulearn_econnect',
                      default=_(u"Habilita el portlet eConnect.")),
        required=False,
        default=False,
    )

    ulearn_portlets_mostvalued = schema.Bool(
        title=_(u'ulearn_most_valued',
                default=_(u"Habilitar portlet Ulearn Most Valued")),
        description=_(u'help_ulearn_most_valued',
                      default=_(u"Habilita el portlet ulearn most valued.")),
        required=False,
        default=False,
    )

    ulearn_portlets_stats = schema.Bool(
        title=_(u'ulearn_stats',
                default=_(u"Habilitar portlet Ulearn Stats")),
        description=_(u'help_ulearn_stats',
                      default=_(u"Habilita el portlet per a veure les estadístiques.")),
        required=False,
        default=True,
    )

    ulearn_portlets_sharedwithme = schema.Bool(
        title=_(u'ulearn_sharedwithme',
                default=_(u"Habilitar portlet compartit amb mi")),
        description=_(u'help_ulearn_sharedwithme',
                      default=_(u"Habilita el portlet per a veure el compartit amb mi.")),
        required=False,
        default=False,
    )

    # ==== FIN Portlets ====


class PortletsSettingsEditForm(controlpanel.RegistryEditForm):
    """MAXUI settings form.
    """
    schema = IPortletsSettings
    id = "PortletsSettingsEditForm"
    label = _(u"Portlets settings")
    description = _(u"help_portlets_settings_editform",
                    default=u"Settings Portlets. Configure allowed Portlets.")

    def updateFields(self):
        super(PortletsSettingsEditForm, self).updateFields()
        # self.fields = self.fields.omit('max_app_token')

    def updateWidgets(self):
        super(PortletsSettingsEditForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

        site = getSite()
        activate_portlets = []
        portlets_slots = ["plone.leftcolumn", "plone.rightcolumn",
                          "genweb.portlets.HomePortletManager1", "genweb.portlets.HomePortletManager2",
                          "genweb.portlets.HomePortletManager3", "genweb.portlets.HomePortletManager4",
                          "genweb.portlets.HomePortletManager5", "genweb.portlets.HomePortletManager6",
                          "genweb.portlets.HomePortletManager7", "genweb.portlets.HomePortletManager8",
                          "genweb.portlets.HomePortletManager9", "genweb.portlets.HomePortletManager10"]

        for manager_name in portlets_slots:
            if 'genweb' in manager_name:
                manager = getUtility(IPortletManager, name=manager_name, context=site['front-page'])
                mapping = getMultiAdapter((site['front-page'], manager), IPortletAssignmentMapping)
                [activate_portlets.append(item[0]) for item in mapping.items()]
            else:
                manager = getUtility(IPortletManager, name=manager_name, context=site)
                mapping = getMultiAdapter((site, manager), IPortletAssignmentMapping)
                [activate_portlets.append(item[0]) for item in mapping.items()]

        portlets = {k: v for k, v in data.iteritems() if 'portlet' in k.lower()}
        if portlets:
            for portlet, value in portlets.iteritems():
                idPortlet = portlet.replace('_', '.')
                namePortlet = portlet.replace('_', ' ')

                if portlet == 'genweb_portlets_news_events_listing':
                    idPortlet = 'genweb.portlets.news_events_listing'
                    namePortlet = 'genweb portlets news_events_listing'

                if value is True:
                    registerPortletType(site,
                                        title=namePortlet,
                                        description=namePortlet,
                                        addview=idPortlet)

                if idPortlet.split('.')[-1] in activate_portlets:
                    value = True
                    data[portlet] = True
                    registerPortletType(site,
                                        title=namePortlet,
                                        description=namePortlet,
                                        addview=idPortlet)
                if value is False:
                    unregisterPortletType(site, idPortlet)

            self.applyChanges(data)

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class PortletsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Portlets settings control panel.
    """
    form = PortletsSettingsEditForm
