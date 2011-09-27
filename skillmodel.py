#!/usr/bin/python

from PySide import QtGui, QtCore

class SkillItemModel(object):
    def __init__(self):
        self.name      = ''
        self.rank      = ''
        self.trait     = ''
        self.is_school = False
        self.emph      = []
        
    def __str__(self):
        return self.name
        
class WeaponItemModel(object):
    def __init__(self):
        self.name  = ''
        self.type  = ''
        self.atk   = ''
        self.dr    = ''
        self.bonus = ''
        
class SkillTableViewModel(QtCore.QAbstractTableModel):
    def __init__(self, dbconn, parent = None):
        super(SkillTableViewModel, self).__init__(parent)        
        self.items = []
        self.headers = ['School Skill', 'Name', 'Rank', 'Trait', 'Emphasis']
        self.text_color = QtGui.QBrush(QtGui.QColor(0x15, 0x15, 0x15))
        self.item_size = QtCore.QSize(32,32)
        self.dbconn = dbconn
        
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.items)
        
    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.headers)
        
    def headerData(self, section, orientation, role = QtCore.Qt.ItemDataRole.DisplayRole):
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:    
            return self.headers[section]
        return None

    def data(self, index, role):
        print index
        print role
        if not index.isValid() or index.row() >= len(self.items):
            return None
        item = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            print 'ask %s' % repr(item)
            if index.column() == 0:
                return item.is_school
            if index.column() == 1:
                return item.name
            if index.column() == 2:
                return item.rank
            if index.column() == 3:
                return item.trait
            if index.column() == 4:
                return ', '.join(item.emph)
        #    elif role == QtCore.Qt.DecorationRole:
        #        if index.column() == 0 and (item['epstatus'] & SHOW_STATUS_NEW == SHOW_STATUS_NEW):
        #            return QtGui.QIcon(':/icons/label_new_red.png')
        #    elif role == QtCore.Qt.UserRole:
        #        return item['showid']
        elif role == QtCore.Qt.ForegroundRole:
            return self.text_color
        elif role == QtCore.Qt.SizeHintRole:
            return self.item_size
        return None
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags            
                
    def need_update(self):
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), 
        self.index(0,0), self.index(len(self.items)-1,0))
        
    def add_item(self, item):
        row = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.append(item)
        self.endInsertRows()
        
    def clean(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()
        
        
    def build_item_model(self, sk_id):
        c = self.dbconn.cursor()
        itm = SkillItemModel()
        c.execute('''SELECT name, attribute FROM skills
                     WHERE uuid=?''', [sk_id])
        for f in c.fetchall():
            itm.name = f[0]
            itm.trait = f[1]
        c.close()
        return itm                
            
    def update_from_model(self, model):
        skills_id_s = model.get_school_skills()
        skills_id_a = model.get_skills( school = False )
        
        self.clean()
        for s in skills_id_s:
            itm = self.build_item_model(s)
            itm.rank = model.get_skill_rank(s)
            itm.is_school = True
            self.add_item(itm)
        for s in skills_id_a:
            itm = self.build_item_model(s)
            itm.rank = model.get_skill_rank(s)
            #self.items.append(itm)
            self.add_item(itm)

            
