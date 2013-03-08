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

class TechItemModel(object):
    def __init__(self):
        self.name        = ''
        self.school_name = ''
        self.rank        = ''
        self.desc        = ''

    def __str__(self):
        return self.name

class TechViewModel(QtCore.QAbstractListModel):
    def __init__(self, dbconn, parent = None):
        super(TechViewModel, self).__init__(parent)

        self.dbconn = dbconn
        self.items = []
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]
        self.item_size = QtCore.QSize(32, 32)

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)
        
    def build_item_model(self, tech_id):
        c = self.dbconn.cursor()
        itm = TechItemModel()
        
        #print 'tech_id: %s' % repr(tech_id)
        
        c.execute('''SELECT school_techs.name, school_techs.rank,
                            schools.name
                            FROM school_techs INNER JOIN schools ON
                            schools.uuid == school_techs.school_uuid
                            WHERE school_techs.uuid=?''', [tech_id])
        for tech_nm, tech_rk, sc_nm in c.fetchall():
            itm.name         = tech_nm
            itm.school_name = sc_nm
            itm.rank        = str(tech_rk)
            break
        c.close()
        return itm        
        
    def add_item(self, item_id):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(self.build_item_model(item_id))
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def update_from_model(self, model):
        self.clean()
        for tech in model.get_techs():
            print tech
            self.add_item(tech)

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
        elif role == QtCore.Qt.UserRole:
            return item
        return None

class TechItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(TechItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            super(TechItemDelegate, self).paint(painter, option, index)
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
        tech_nm      = item.name
        tech_nm_rect = font_metric.boundingRect(tech_nm)

        text_pen = QtGui.QPen(text_color, 1)

        painter.setPen(text_pen)
        painter.drawText(left_margin + option.rect.left(), option.rect.top() + tech_nm_rect.height(), tech_nm)

        # paint adv type & cost
        painter.setFont(sub_font)
        font_metric    = painter.fontMetrics()
        school_nm      = item.school_name
        school_nm_rect = font_metric.boundingRect(school_nm)
        painter.drawText(left_margin + option.rect.left(),
                         option.rect.top() + tech_nm_rect.height() + school_nm_rect.height(),
                         school_nm)

        circle_pen = QtGui.QPen(text_color, 2)
        painter.setPen(circle_pen)
        rank      = item.rank
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
