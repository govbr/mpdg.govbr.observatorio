# -*- coding: utf-8 -*
from collective.cover.utils import assign_tile_ids
from plone.tiles.interfaces import ITileDataManager
import json

class MakeLayout(object):

    def __init__(self,cover):
        super(MakeLayout, self).__init__()
        self.cover = cover
        self.tiles = {}
        self._make_tiles()
        self._layout = self._make_layout()
        self._bootstrap_tiles()
        self._populate_tiles()

    def _make_tiles(self):
        self.tiles = {'header' : LTile("standaloneheader")}

    def _layout_skeleton(self):
        return LLayout(
            LRow(
                LColumn(16,
                    self.tiles['header'],
                    LTile("sharing")
                )
            ),
        )

    def _make_layout(self):
        return self._layout_skeleton().result()

    def get_layout(self):
        return self._layout

    def get_tile(self,name):
        return self.tiles[name].get_tile()

    def _bootstrap_tiles(self):
        layout = self.get_layout()
        assign_tile_ids(layout, override=False)
        self.cover.cover_layout = json.dumps(layout)
        self.cover.reindexObject()

    def update_tile(self,tile_name,attrs={},conf={}):
        self.tiles[tile_name].update(attrs,conf)

    def update_tile_header(self,tile_name,title,css_class,htmltag=u'h2'):
        attrs = {'title':title}
        conf = {
            'css_class':css_class,
            'title': {'htmltag': htmltag}
        }
        self.update_tile(tile_name,attrs,conf)

    def update_tile_header_link(self,tile_name,title,css_class,htmltag=u'h2'):
        attrs = {'link_text':title}
        conf = {'css_class':css_class}
        self.update_tile(tile_name,attrs,conf)

    def _populate_tiles(self):
        self.update_tile_header("header", self.cover.Title(), "verde-escuro")


class LLayout(object):
    def __init__(self,*children):
        super(LLayout, self).__init__()
        self.children = children

    def result(self):
        return [row.result() for row in self.children]


class LRow(object):
    def __init__(self,*children):
        super(LRow, self).__init__()
        self.children = children

    def result(self):
        return {
            "type": 'row',
            'children' : [col.result() for col in self.children]
        }


class LColumn(object):
    def __init__(self,size,*children):
        super(LColumn, self).__init__()
        self.size = size
        self.children=children
        self.roles = ["Manager"]

    def result(self):
        return {
            "data": {
                "layout-type": "column",
                "column-size": self.size
            },
            "type": "group",
            "roles" : self.roles,
            "children": [tile.result() for tile in self.children]
        }


class LTile(object):
    def __init__(self,context,tile_type="standaloneheader",tile_id=''):
        self.context = context
        super(LTile, self).__init__()
        self.dic = {
            "tile-type": tile_type,
            "type": "tile",
            "id":tile_id
        }

    def get_tile(self):
        txt = '{0}/{1}'.format(self.dic['tile-type'],self.dic['id'])
        return self.context.restrictedTraverse(txt)

    def _update_attrs(self,tile,attrs):
        data = ITileDataManager(tile)
        data.set(attrs)

    def _update_conf(self,tile,attrs):
        conf = tile.get_tile_configuration()
        conf.update(attrs)
        tile.set_tile_configuration(conf)

    def update(self,attrs={},conf={}):
        tile = self.get_tile()
        if attrs:
            self._update_attrs(tile, attrs)
        if conf:
            self._update_conf(tile, conf)

    def result(self):
        return self.dic