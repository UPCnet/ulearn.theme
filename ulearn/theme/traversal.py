from plone.resource.traversal import ResourceTraverser


class UlearnTraverser(ResourceTraverser):
    """The Ulearn theme traverser.

    Allows traversal to /++ulearn++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'ulearn'
