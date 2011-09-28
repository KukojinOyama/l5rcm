#!/usr/bin/python

from PySide import QtCore, QtGui

class Advancement(object):
    def __init__(self, tag, cost):
        self.type  = tag
        self.cost  = cost
        self.desc  = ''

    def __str__(self):
        return self.desc

class AttribAdv(Advancement):
    def __init__(self, attrib, cost):
        super(AttribAdv, self).__init__('attrib', cost)
        self.attrib = attrib

class VoidAdv(Advancement):
    def __init__(self, cost):
        super(VoidAdv, self).__init__('void', cost)

class SkillAdv(Advancement):
    def __init__(self, skill, cost):
        super(SkillAdv, self).__init__('skill', cost)
        self.skill = skill

class AdvancementViewModel(QtCore.QAbstractListModel):
    def __init__(self, parent = None):
        super(AdvancementViewModel, self).__init__(parent)

        self.items = []
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.bg_color   = [ QtGui.QBrush(QtGui.QColor(0xFF, 0xEB, 0x82)),
                            QtGui.QBrush(QtGui.QColor(0xEB, 0xFF, 0x82)) ]
        self.item_size = QtCore.QSize(32, 32)

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)

    def add_item(self, item):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(item)
        self.endInsertRows()

    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def update_from_model(self, model):
        self.clean()
        for adv in reversed(model.advans):
            self.add_item(adv)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return item.type
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.BackgroundRole:
            return self.bg_color[ index.row() % 2 ]
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        elif role == QtCore.Qt.UserRole:
            return item
        return None

class AdvancementItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(AdvancementItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid():
            super(AdvancementItemDelegate, self).paint(painter, option, index)
            return

        item       = index.data(QtCore.Qt.UserRole)
        text_color = index.data(QtCore.Qt.ForegroundRole)
        bg_color   = index.data(QtCore.Qt.BackgroundRole)
        hg_color   = QtGui.QBrush(bg_color)
        hg_color.setStyle(QtCore.Qt.Dense3Pattern)

        painter.save()

        # fill the background color
        if option.state & QtGui.QStyle.State_Selected == QtGui.QStyle.State_Selected:
             painter.fillRect(option.rect, option.palette.highlight())
             text_color = option.palette.highlightedText()
        else:
            painter.fillRect(option.rect, bg_color)

        painter.setPen(QtCore.Qt.DashLine)
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        main_font = painter.font()
        sub_font = QtGui.QFont().resolve(main_font)
        sub_font.setPointSize(7)

        left_margin = 15

        # paint the airdate with a smaller font over the item name
        # suppose to have 24 pixels in vertical
        painter.setFont(sub_font)
        font_metric = painter.fontMetrics()
        adv_tp      = item.type
        adv_tp_rect = font_metric.boundingRect(adv_tp)

        text_pen = QtGui.QPen(text_color, 1)

        painter.setPen(text_pen)
        painter.drawText(left_margin + option.rect.left(), option.rect.top() + adv_tp_rect.height(), adv_tp)

        # paint adv type & cost
        main_font.setBold(True)
        painter.setFont(main_font)
        font_metric = painter.fontMetrics()
        tmp         = str(item).split(',')
        adv_nm      = tmp[0]
        adv_nm_rect = font_metric.boundingRect(adv_nm)
        painter.drawText(left_margin + option.rect.left(), option.rect.top() + adv_tp_rect.height() + adv_nm_rect.height(), adv_nm)

        main_font.setBold(False)
        painter.setFont(main_font)
        adv_nm      = tmp[1]
        adv_nm_rect = font_metric.boundingRect(adv_nm)
        painter.drawText(option.rect.right()-150, option.rect.top() + adv_tp_rect.height() + adv_nm_rect.height(), adv_nm)

        painter.restore()
