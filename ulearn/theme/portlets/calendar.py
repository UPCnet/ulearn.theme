from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_chain
from genweb.core.interfaces import IHomePage

from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.view import memoize_contextless
from plone.app.portlets.portlets.calendar import Renderer as calendarRenderer

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from ulearn.core.content.community import ICommunity
from ulearn.core.interfaces import IEventsFolder

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

    def today(self):
        today = {}
        today['weekday'] = PLMF(self._ts.day_msgid(self.now.tm_wday+1, format='l'))
        today['number'] = self.now.tm_mday
        return today

    @memoize_contextless
    def get_nearest_today_event(self):
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        now = DateTime()
        tomorrow = DateTime.Date(now + 1)
        yesterday = DateTime.Date(now - 1)

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or IPloneSiteRoot.providedBy(self.context):
            path = navigation_root_path
        else:
            path = '/'.join(self.get_community().getPhysicalPath())

        query = {
            'portal_type': self.calendar.getCalendarTypes(),
            'review_state': self.calendar.getCalendarStates(),
            'start': {'query': [yesterday, tomorrow], 'range': 'min:max'},
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
        now = DateTime()
        year = self.year
        month = self.month
        year = int(year)
        month = int(month)
        last_day = self.calendar._getCalendar().monthrange(year, month)[1]
        last_date = self.calendar.getBeginAndEndTimes(last_day, month, year)[1]

        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or IPloneSiteRoot.providedBy(self.context):
            path = navigation_root_path
        else:
            path = '/'.join(self.get_community().getPhysicalPath())

        query = {
            'portal_type': self.calendar.getCalendarTypes(),
            'review_state': self.calendar.getCalendarStates(),
            'start': {'query': last_date, 'range': 'max'},
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
            'path': path,
        }

        result = pc(**query)
        nearest = self.get_nearest_today_event()
        return [event for event in result if event.id != nearest.id]

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()

        if IHomePage.providedBy(self.context) or IPloneSiteRoot.providedBy(self.context):
            path = navigation_root_path
        else:
            path = '/'.join(self.get_community().getPhysicalPath())

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
                    day['eventstring'] = '\n'.join(localized_date+[' %s' %
                        self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def get_community(self):
        context = aq_inner(self.context)
        for obj in aq_chain(context):
            if ICommunity.providedBy(obj):
                return obj

    def show_newevent_url(self):
        context = aq_inner(self.context)
        if IHomePage.providedBy(context) or IPloneSiteRoot.providedBy(self.context):
            return False
        else:
            return True

    def newevent_url(self):
        community = self.get_community()
        event_folder_id = ''
        for obj_id in community.objectIds():
            if IEventsFolder.providedBy(community[obj_id]):
                event_folder_id = obj_id

        return '{}/{}/++add++Event'.format(self.get_community().absolute_url(), event_folder_id)


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
