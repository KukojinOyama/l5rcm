#!/usr/bin/python

import sys, os
import sqlite3

def create(dbfile):
    try:
        dbconn = sqlite3.connect(dbfile)
        c = dbconn.cursor()

        # clans
        c.execute('''create table clans
        (uuid INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        
        # families
        c.execute('''create table families
        (uuid INTEGER PRIMARY KEY, name TEXT UNIQUE, clan_id INTEGER,
        perk TEXT, perkval INTEGER)''')

        # schools
        c.execute('''create table schools
        (uuid INTEGER PRIMARY KEY, name TEXT UNIQUE, tag TEXT,
        clan_id INTEGER, perk TEXT, perkval INTEGER, honor NUMERIC, 
        affinity TEXT, deficiency TEXT)''')

        # skills
        c.execute('''create table skills
        (uuid INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT,
        attribute TEXT)''')

        # school skills       
        c.execute('''create table school_skills
        (school_uuid INTEGER, skill_uuid INTEGER, skill_rank INTEGER,
        PRIMARY KEY(school_uuid, skill_uuid))''')

        # tags
        c.execute('''create table tags
        (uuid integer PRIMARY KEY, tag TEXT)''')       
        
        # cnt
        c.execute('''create table cnt
        (name varchar PRIMARY KEY, value INTEGER)''')

        # save (commit) and close the cursor
        dbconn.commit()
        c.close()
        return True
    except:
        print 'database creation failed'
        return False

def connect(dbfile):
    return sqlite3.connect(dbfile)

def query(conn, query, data = None, print_error = True):
    c = conn.cursor()
    result = None
    try:
        if data is not None:
            c.execute(query, data)
        else:
            c.execute(query)
        result = c.fetchall()
    except Exception as e:
        if print_error:
            print e
    finally:
        c.close()
    return result

def non_query(conn, query, data = None, print_error = True):   
    c = conn.cursor()
    recs = 0
    try:
        if data is not None:
            recs = c.execute(query, data)
        else:
            recs = c.execute(query)
    except Exception as e:
        if print_error:
            print e
    finally:
        c.close()
    return recs

def get_cnt(conn, cnt):
    # increment value in cnt
    if non_query(conn, '''insert into cnt values(?,1)''', [cnt], False) == 0:
        if non_query(conn, '''update cnt SET value=value+1 WHERE name=?''', [cnt]) == 0:
            print 'insert cnt failed'
            return 0

    val = query(conn, '''select value from cnt where name=?''', [cnt])

    if val is not None and len(val) == 1:
        #conn.commit()
        return int(val[0][0])
    return 0
    
def add_tag(uuid, tag):    
    if non_query(dbconn, '''insert into tags values (?,?)''', [uuid,tag]):
        print 'add tag %s to %d' % (tag, uuid)
    else:
        print 'tag %s already exists for uuid %d' % uuid

def import_clans(dbconn, path):
    f = open( os.path.join(path, 'names'), 'rt' )
    for name in f:
        uuid = get_cnt(dbconn, 'uuid')
        name = name.strip()
        if non_query(dbconn, '''insert into clans values (?,?)''', [uuid,name]) == 1:
            print 'imported clan %s with uuid %s' % (name, uuid)
    f.close()

def import_clan_families(dbconn, clan, path):
    print 'import %s clan families' % clan

    # get clan uuid
    print 'search uuid for clan %s' % clan
    clanuid = query(dbconn, '''select uuid from clans where name=?''', [clan])
    if clanuid is not None and len(clanuid) > 0:
        clanuid = clanuid[0][0]
    
    f = open( path, 'rt' )
    while True:
        if not f.readline().startswith('#'): break
        name = f.readline().strip()
        perk = f.readline().strip()
        perkval = f.readline().strip()
        
        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into families values(?,?,?,?,?)''',
                             [uuid,name,clanuid,perk,perkval]):
            print 'imported family %s with uuid %s' % (name, uuid)
    f.close()

def import_clan_schools(dbconn, clan, path):
    print 'import %s clan schools' % clan

    # get clan uuid    
    print 'search uuid for clan %s' % clan
    clanuid = query(dbconn, '''select uuid from clans where name=?''', [clan])
    if clanuid is not None and len(clanuid) > 0:
        clanuid = clanuid[0][0]
    
    f = open( path, 'rt' )
    while True:
        if not f.readline().startswith('#'): break
        name = f.readline().strip()
        tag = f.readline().strip()
        perk, perkval = f.readline().split()
        honor, honor_val = f.readline().split()
        affin = f.readline()
        defic = f.readline()
        if affin.startswith('-'): affin = None
        if defic.startswith('-'): defic = None

        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into schools values(?,?,?,?,?,?,?,?,?)''',
                             [uuid,name,tag,clanuid,perk,perkval,honor_val,affin,defic]):
            print 'imported school %s with uuid %s' % (name, uuid)
        else:
            print 'cannot import school %s' % name
    f.close()

def import_categ_skills(dbconn, categ, path):
    print 'import %s skills' % categ
   
    f = open( path, 'rt' )
    for line in f:
        tokens = line.split()
        if len(tokens) < 2:
            continue
        name = tokens[0].replace('_', ' ')
        attrib = tokens[1]
        tags = tokens[2: len(tokens)-2]

        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into skills values(?,?,?,?)''',
                             [uuid,name,categ,attrib]):
            print 'imported school %s with uuid %s' % (name, uuid)
            
            for t in tags:
                add_tag(uuid, t)
        else:
            print 'cannot import skill %s' % name
    f.close()

def import_families(conn, path):
    for path, dirs, files in os.walk(path):
        for file_ in files:
            import_clan_families(conn, file_, os.path.join(path, file_))

def import_schools(conn, path):
    for path, dirs, files in os.walk(path):
        for file_ in files:
            import_clan_schools(conn, file_, os.path.join(path, file_))
            
def import_skills(conn, path):
    for path, dirs, files in os.walk(path):
        for file_ in files:
            import_categ_skills(conn, file_.lower(), os.path.join(path, file_))            

def importdb(conn, path):
    import_clans(conn, os.path.join(path, 'clans'))
    import_families(conn, os.path.join(path, 'families'))
    import_schools(conn, os.path.join(path, 'schools'))
    import_skills(conn, os.path.join(path, 'skills'))
    conn.commit()

### MAIN ###

def main():
    run = True
    dbconn = None
    while run:
        print '''Choose:
                  1. create db
                  2. list clans
                  3. list families
                  4. list schools
                  c. connect db
                  i. import db
               '''
        c = raw_input()
        if c == 'q':
            run = False
            break
        if c == 'c':
            print 'insert db file: [l5rdb.sqlite]'
            path = raw_input()
            if len(path) == 0: path = 'l5rdb.sqlite'
            dbconn = connect(path)
        elif c == 'i':
            print 'insert import path: [./import/]'
            path = raw_input()
            if len(path) == 0: path = './import/'
            importdb(dbconn, path)
        elif c == '1':
            print 'insert db file: [l5rdb.sqlite]'
            path = raw_input()
            if len(path) == 0: path = 'l5rdb.sqlite'
            if create(path): print 'ok'
            else: print 'ko'
        elif c == '2':
            if dbconn is None:
                print 'not connected'
            else:
                clans = query(dbconn, '''select * from clans''')
                if clans is None or len(clans) == 0: print 'no clans'; continue
                print 'clans:'
                for clan in clans:
                    print clan
        elif c == '3':
            if dbconn is None:
                print 'not connected'
            else:
                fams = query(dbconn, '''select uuid,name from families''')
                if fams is None or len(fams) == 0: print 'no families'; continue
                print 'families:'
                for fam in fams:
                    print fam
        elif c == '4':
            if dbconn is None:
                print 'not connected'
            else:
                fams = query(dbconn, '''select * from schools''')
                if fams is None or len(fams) == 0: print 'no schools'; continue
                print 'schools:'
                for fam in fams:
                    print fam

        if dbconn is not None:
            dbconn.commit()

if __name__ == '__main__':
    main()
