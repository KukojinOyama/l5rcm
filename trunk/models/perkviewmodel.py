# -*- coding: iso-8859-1 -*-
# Copyright (C) 2011 Daniele Simonetti
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from PySide import QtGui, QtCore

class PerkItemModel(object):
    def __init__(self):
        self.name        = ''
        self.cost        = ''
        self.rank        = ''
        self.tag         = ''
        self.notes       = ''

    def __str__(self):
        return self.name

class PerkViewModel(QtCore.QAbstractListModel):
    def __init__(self, dbconn, type_, parent = None):
        super(PerkViewModel, self).__init__(parent)

        self.dbconn = dbconn
        self.items = []
        self.type  = type_
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]
        self.item_size = QtCore.QSize(32, 32)

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)       
        
    def build_item_model(self, model, perk_id):
        c = self.dbconn.cursor()
        itm = PerkItemModel()
               
        c.execute('''SELECT uuid, name FROM perks
                     WHERE uuid=?''', [perk_id])
        
        for uuid, perk_nm in c.fetchall():
            itm.name        = perk_nm
            itm.rank, itm.cost, itm.tag, itm.notes = model.get_perk_info( uuid )
            break
        c.close()
        return itm        
        
    def add_item(self, model, item_id):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(self.build_item_model(model, item_id))
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def update_from_model(self, model):
        self.clean()
        if self.type == 'merit':
            for perk in model.get_merits():
                self.add_item(model, perk)
        else:
            for perk in model.get_flaws():
                self.add_item(model, perk)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[ index.row() % 2 ]
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        elif role == QtCore.Qt.ToolTipRole:
            return item.notes
        elif role == QtCore.Qt.UserRole:
            return item
        return None

class PerkItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(PerkItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            super(PerkItemDelegate, self).paint(painter, option, index)
            return

        item       = index.data(QtCore.Qt.UserRole)
        text_color = index.data(QtCore.Qt.ForegroundRole)
        bg_color   = index.data(QtCore.Qt.BackgroundRole)
        hg_color   = QtGui.QBrush(bg_color)
        hg_color.setStyle(QtCore.Qt.Dense3Pattern)

        painter.save()
        
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True);

        # fill the background color
        if option.state & QtGui.QStyle.State_Selected == QtGui.QStyle.State_Selected:
             painter.fillRect(option.rect, option.palette.highlight())
             text_color = option.palette.highlightedText()
        else:
            painter.fillRect(option.rect, bg_color)

        grid_pen = QtGui.QPen( QtCore.Qt.lightGray, 1 )
        painter.setPen(grid_pen)
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        main_font = painter.font()
        sub_font = QtGui.QFont().resolve(main_font)
        sub_font.setPointSize(7)

        left_margin = 15

        # paint the airdate with a smaller font over the item name
        # suppose to have 24 pixels in vertical
        main_font.setBold(True)
        painter.setFont(main_font)
        font_metric = painter.fontMetrics()
        perk_nm      = item.name
        perk_nm_rect = font_metric.boundingRect(perk_nm)

        text_pen = QtGui.QPen(text_color, 1)

        painter.setPen(text_pen)
        painter.drawText(left_margin + option.rect.left(), option.rect.top() + perk_nm_rect.height(), perk_nm)

        if item.tag:
            # paint adv type & cost
            painter.setFont(sub_font)
            font_metric    = painter.fontMetrics()
            tag_nm         = item.tag
            tag_nm_rect = font_metric.boundingRect(tag_nm)
            painter.drawText(left_margin + option.rect.left(),
                             option.rect.top() + perk_nm_rect.height() + tag_nm_rect.height(),
                             tag_nm)

        circle_pen = QtGui.QPen(text_color, 2)
        painter.setPen(circle_pen)
        rank      = str(item.rank)
        rank_rect = font_metric.boundingRect(rank)
        circle_rect = QtCore.QRectF( float(option.rect.right()-option.rect.height()-left_margin),
                                     float(option.rect.top() + 4),
                                     float(option.rect.height()-8), float(option.rect.height()-8) )
                                            
                                            
        painter.drawEllipse( circle_rect )

        main_font.setBold(True)
        painter.setFont(main_font)
        painter.setPen(text_pen)
        painter.drawText(circle_rect.adjusted(8, 3.5, 0, 0), rank)

        painter.restore()
