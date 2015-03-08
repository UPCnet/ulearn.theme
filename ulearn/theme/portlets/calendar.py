from plone import api
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_chain
from genweb.core.interfaces import IHomePage

from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.view import memoize_contextless

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from ulearn.core.content.community import ICommunity
from ulearn.core.interfaces import IEventsFolder
from plone.app.event.portlets.portlet_calendar import Renderer as calendarRenderer
from plone.app.event.base import localized_today, localized_now, dt_start_of_day, dt_end_of_day
from plone.dexterity.interfaces import IDexterityContent

from DateTime import DateTime
from zope.i18nmessageid import MessageFactory
PLMF = MessageFactory('plonelocales')


class ICalendarPortlet(IPortletDataProvider):
    """ A portlet which can render the logged user profile information.
    """


class Assignment(base.Assignment):
    implements(ICalendarPortlet)

    title = _(u'ulearncalendar', default=u'Calendar portlet')


class Renderer(calendarRenderer):

    render = ViewPageTemplateFile('templates/calendar.pt')

    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)

        if IHomePage.providedBy(self.context) or \
           IPloneSiteRoot.providedBy(self.context) or \
           not IDexterityContent.providedBy(self.context):
            path = ''
        else:
            if ICommunity.providedBy(aq_inner(self.context)):
                community = aq_inner(self.context)
                portal = api.portal.get()
                portal_path = portal.getPhysicalPath()
                community_path = community.getPhysicalPath()
                path = '/' + '/'.join(set(community_path) - set(portal_path))
            else:
                path = ''
        self.data.search_base = path
        self.data.state = ('published', 'intranet')

        self.username = api.user.get_current().id
        # self.user_info = get_safe_member_by_id(self.username)

    def today(self):
        today = {}
        loc_today = localized_today(self.context)
        weekday = loc_today.isoweekday()
        today['weekday'] = PLMF(self._ts.day_msgid(0 if weekday == 7 else weekday, format='l'))
        today['number'] = loc_today.day
        return today

    @memoize_contextless
    def get_nearest_today_event(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = localized_now()

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or \
           IPloneSiteRoot.providedBy(self.context) or\
           not IDexterityContent.providedBy(self.context):
            path = navigation_root_path
        else:
            if ICommunity.providedBy(aq_inner(self.context)):
                community = aq_inner(self.context)
                path = '/'.join(community.getPhysicalPath())
            else:
                path = navigation_root_path

        query = {
            'portal_type': 'Event',
            'review_state': self.data.state,
            'start': {'query': [now, dt_end_of_day(now)], 'range': 'min:max'},
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': path,
            'sort_limit': 1
        }

        result = pc(**query)
        if result:
            return result[0]
        else:
            return

    def get_next_three_events(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = localized_now()

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or \
           IPloneSiteRoot.providedBy(self.context) or \
           not IDexterityContent.providedBy(self.context):
            path = navigation_root_path
        else:
            if ICommunity.providedBy(aq_inner(self.context)):
                community = aq_inner(self.context)
                path = '/'.join(community.getPhysicalPath())
            else:
                path = navigation_root_path

        query = {
            'portal_type': 'Event',
            'review_state': self.data.state,
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': path,
        }

        result = pc(**query)
        nearest = self.get_nearest_today_event()
        if nearest:
            return [event for event in result if event.id != nearest.id]
        else:
            return result[:3]

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or IPloneSiteRoot.providedBy(self.context):
            path = navigation_root_path
        else:
            if ICommunity.providedBy(aq_inner(self.context)):
                community = aq_inner(self.context)
                path = '/'.join(community.getPhysicalPath())
            else:
                path = navigation_root_path

        weeks = self.calendar.getEventsForCalendar(month, year, path=path)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date + [' %s' %
                        self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def show_newevent_url(self):
        """ Assume that the calendar is only shown on the community itself. """
        context = aq_inner(self.context)
        if IHomePage.providedBy(context) or IPloneSiteRoot.providedBy(self.context):
            return False
        else:
            user_roles = context.get_local_roles_for_userid(self.username)
            if 'Editor' in user_roles:
                return True
            else:
                return False

    def newevent_url(self):
        """ Assume that the new event button is only shown on the community itself. """
        context = aq_inner(self.context)
        # Fist, a light guard
        if ICommunity.providedBy(context):
            event_folder_id = ''
            for obj_id in context.objectIds():
                if IEventsFolder.providedBy(context[obj_id]):
                    event_folder_id = obj_id

            return '{}/{}/++add++Event'.format(context.absolute_url(), event_folder_id)
        else:
            return ''

    def is_community(self):
        """ Assume that the calendar is only shown on the community itself. """
        context = aq_inner(self.context)
        if ICommunity.providedBy(context):
            return True
        else:
            return False

    def get_event_folder_url(self):
        """ Assume that the new event button is only shown on the community itself. """
        context = aq_inner(self.context)
        return '{}/events'.format(context.absolute_url())


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
