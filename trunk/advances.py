#!/usr/bin/python

class Advancement(object):
    def __init__(self, tag, cost):
        self.type = tag
        self.cost = cost

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

