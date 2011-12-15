#!/usr/bin/python
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

def get_mastery_ability_rule(dbconn, skill_id, rank):
    c = dbconn.cursor()
    c.execute('''select skill_rank, rule from mastery_abilities
                 where skill_uuid=? and skill_rank=?''', [skill_id, rank])
    rule_ = None
    for rank, rule in c.fetchall():
        rule_ = rule
    c.close()
    return rule_

    