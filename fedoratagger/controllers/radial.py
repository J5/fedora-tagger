# -*- coding: utf-8 -*-

# turbogears imports
from tg import expose, flash, redirect, request, url

# project specific imports
from fedoratagger.lib.base import BaseController
from fedoratagger.model import DBSession, metadata
from fedoratagger import model as m

import sqlalchemy
import random

from tw2.jit import SQLARadialGraph
from tw2.core import JSSymbol

class RadialController(BaseController):

    @expose('fedoratagger.templates.profile')
    def index(self, **kw):
        """ Handles the ``/radial`` URL. """

        n = m.Package.query.count()
        i = random.randint(0, n-1)

        # TODO -- There must be a better way
        package = m.Package.query.all()[i]

        name = package.name

        redirect('/radial/%s' % name, **kw)

    @expose('json')
    def data(self, *args, **kw):
        class TaggerSQLARadialGraph(SQLARadialGraph):
            id = 'sqlaRadialGraph'
            base_url = '/radial/data/'
            entities = [m.Package, m.Tag, m.TagLabel]

            show_attributes = False
            show_empty_relations = False

            alphabetize_relations = 24
            alphabetize_minimal = True

        jitwidget = TaggerSQLARadialGraph
        resp = jitwidget.request(request)
        return resp.body

    @expose('fedoratagger.templates.widget')
    def _default(self, *args, **kw):
        """ Serves up the RadialGraph widget """

        assert(len(args) == 1) # how else could it be?
        name = args[0]

        base = DBSession.query(m.Package).filter_by(name=name)

        if base.count() == 0 :
            flash("No such package '%s'" % name, status='error')
            redirect('/')

        if base.count() > 1:
            raise LookupError, "More than one package matches '%s'" % name

        package = base.one()

        # Some color constants for the radial graph
        bg = '#F8F7ED'
        green = '#84CA24'
        blue = '#006295'

        class TaggerSQLARadialGraph(SQLARadialGraph):
            id = 'sqlaRadialGraph'
            base_url = '/radial/data/'
            entities = [m.Package, m.Tag, m.TagLabel]
            rootObject = package

            # Have it occupy the full page
            width = '980'
            height = '980'

            # Have it conform with the site style
            backgroundcolor = bg
            background = { 'CanvasStyles': { 'strokeStyle' : bg } }
            Node = { 'color' : green }
            Edge = { 'color' : blue, 'lineWidth':1.5, }

            # Space things out a little
            levelDistance = 150

            # Override the label style
            onPlaceLabel = JSSymbol(src="""
                (function(domElement, node){
                    domElement.style.display = "none";
                    domElement.innerHTML = node.name;
                    domElement.style.display = "";
                    var left = parseInt(domElement.style.left);
                    domElement.style.width = '120px';
                    domElement.style.height = '';
                    var w = domElement.offsetWidth;
                    domElement.style.left = (left - w /2) + 'px';

                    // This should all be moved to a css file
                    domElement.style.cursor = 'pointer';
                    if ( node._depth <= 1 )
                        domElement.style.color = 'black';
                    else
                        domElement.style.color = 'grey';
                })""")

        return {'widget': TaggerSQLARadialGraph}
