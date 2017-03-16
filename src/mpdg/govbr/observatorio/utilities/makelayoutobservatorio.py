from mpdg.govbr.observatorio.utilities.makelayout import MakeLayout, LTile, LColumn, LLayout, LRow


class MakeLayoutObservatorio(MakeLayout):
    def _make_tiles(self):
        self.tiles['header'] = LTile(self.cover,"standaloneheader")

    def _layout_skeleton(self):
        return LLayout(
            LRow(
                LColumn(16,
                    self.tiles['header']
                )
            ),
        )

    def _populate_tiles(self):
        obj = self.cover.aq_parent
        cor = "verde-escuro"
        if hasattr(obj,'getCor'):
            cor = obj.getCor()

        self.update_tile_header("header", obj.Title(), cor)