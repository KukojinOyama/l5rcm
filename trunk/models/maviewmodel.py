﻿#!/usr/bin/python

from PySide import QtGui, QtCore

class MaItemModel(object):
    def __init__(self):
        self.skill       = ''
        self.skill_rank  = ''
        self.desc        = ''

    def __str__(self):
        return self.desc

class MaViewModel(QtCore.QAbstractListModel):
    def __init__(self, dbconn, parent = None):
        super(MaViewModel, self).__init__(parent)

        self.dbconn = dbconn
        self.items = []
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]
        self.item_size = QtCore.QSize(32, 32)

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)         
        
    def add_item(self, sk_name, sk_rnk, ma_brief):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)

        itm = MaItemModel()   
        itm.skill_name = sk_name
        itm.skill_rank = str(sk_rnk)
        itm.desc       = ma_brief
        
        self.items.append(itm)
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def get_mastery_abilities(self, model):
        c = self.dbconn.cursor()
        
        for sk_uuid in model.get_skills():
            sk_rank = model.get_skill_rank(sk_uuid)
            
            c.execute('''SELECT skills.name, mastery_abilities.skill_rank, mastery_abilities.brief
                         FROM mastery_abilities INNER JOIN skills
                         ON skills.uuid=mastery_abilities.skill_uuid
                         WHERE skills.uuid=? and mastery_abilities.skill_rank<=?''', 
                         [sk_uuid, sk_rank])
                        
            for name, rank, brief in c.fetchall():
                yield name, rank, brief
            
        c.close()    
        
    def update_from_model(self, model):
        self.clean()
        for sk_name, sk_rnk, ma_brief in self.get_mastery_abilities(model):
            self.add_item(sk_name, sk_rnk, ma_brief)

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

class MaItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(MaItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            super(MaItemDelegate, self).paint(painter, option, index)
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
        sk_nm       = item.skill_name
        sk_nm_rect = font_metric.boundingRect(sk_nm)

        text_pen = QtGui.QPen(text_color, 1)

        painter.setPen(text_pen)
        painter.drawText(left_margin + option.rect.left(), option.rect.top() + sk_nm_rect.height(), sk_nm)

        # paint adv type & cost
        painter.setFont(sub_font)
        font_metric    = painter.fontMetrics()
        ma_brief       = item.desc
        ma_brief_rect  = font_metric.boundingRect(ma_brief)
        painter.drawText(left_margin + option.rect.left(),
                         option.rect.top() + sk_nm_rect.height() + ma_brief_rect.height(),
                         ma_brief)

        circle_pen = QtGui.QPen(text_color, 2)
        painter.setPen(circle_pen)
        rank      = item.skill_rank
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
