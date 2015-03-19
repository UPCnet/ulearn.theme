# -*- coding: utf-8 -*-
from five.grok import adapter
from five.grok import implementer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets.base import IPortletRenderer
from genweb.smartportlet.renderers.interfaces import IPortletItemRenderer
from genweb.smartportlet.renderers.interfaces import IPortletContainerRenderer
from genweb.smartportlet.renderers import PortletItemRenderer
from genweb.smartportlet.renderers import PortletContainerRenderer
from ulearn.core.content.video_embed import IVideoEmbed
from plone.app.contenttypes.interfaces import IImage

import re

YOUTUBE_REGEX = re.compile(r'youtube.*?(?:v=|embed\/)([\w\d-]+)', re.IGNORECASE)


@adapter(IVideoEmbed)
@implementer(IPortletItemRenderer)
class VideoPortletItemRenderer(PortletItemRenderer):
    title = "Video view"
    css_class = 'carousel-video'

    @property
    def template(self):
        embed_type, code = self.getEmbed()
        try:
            template = ViewPageTemplateFile('templates/{}.pt'.format(embed_type))
        except ValueError:
            template = ViewPageTemplateFile('templates/default.pt')
        return template

    def getVideo(self):
        embed_type, code = self.getEmbed()
        return code

    def getEmbed(self):
        is_youtube_video = YOUTUBE_REGEX.search(self.item.video_url)
        if is_youtube_video:
            return ('youtube', is_youtube_video.groups()[0])

        return (None, None)


@adapter(IPortletRenderer, name='carousel_container_renderer')
@implementer(IPortletContainerRenderer)
class CarouselPortletContainerRenderer(PortletContainerRenderer):
    title = "Carousel view"
    template = ViewPageTemplateFile('templates/carousel-container.pt')
    css_class = 'carousel-container-div'


@adapter(IImage)
@implementer(IPortletItemRenderer)
class ImagePortletItemRenderer(PortletItemRenderer):
    title = "Image view"
    template = ViewPageTemplateFile('templates/image.pt')
    css_class = 'carousel-image'
