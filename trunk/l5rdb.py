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
         wildcard TEXT, emphases TEXT,
         PRIMARY KEY(school_uuid, skill_uuid, wildcard))''')

        # weapons
        c.execute('''create table weapons
        (uuid INTEGER PRIMARY KEY, name TEXT, skill_uuid INTEGER,
         dr TEXT, dr_alt TEXT, range INTEGER, strength INTEGER,
         min_strength INTEGER, effect_id INTEGER, cost TEXT)''')

        # armors
        c.execute('''create table armors
        (uuid INTEGER PRIMARY KEY, name TEXT, tn INTEGER,
         rd INTEGER, special TEXT, cost TEXT)''')
        
        # tags
        c.execute('''create table tags
        (uuid INTEGER, tag VARCHAR, PRIMARY KEY(uuid, tag))''')

        # effects
        c.execute('''create table effects
        (uuid INTEGER PRIMARY KEY, tag VARCHAR UNIQUE, desc TEXT)''')

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

def value_or_null(value):
    if value is None or value.startswith('-'):
        return None
    return value.strip()

def parse_skill_line(sl):
    tk = sl.strip().split()
    sk_name = tk[0].replace('_', ' ')
    sk_rank = 1
    sk_emph = None
    if len(tk) > 1:
        for i in xrange(1, len(tk)):
            if tk[i].startswith('?'):
                sk_rank = int(tk[i][1])
            elif tk[i].startswith('('):
                sk_emph = tk[i].strip('()').replace('_', ' ')
    return sk_name, sk_rank, sk_emph

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

def add_tag(dbconn, uuid, tag):
    if non_query(dbconn, '''insert into tags values (?,?)''', [uuid,tag]):
        print 'add tag %s to %d' % (tag, uuid)
    else:
        print 'tag %s already exists for uuid %d' % (tag, uuid)

def import_clans(dbconn, path):
    f = open( os.path.join(path, 'names'), 'rt' )
    for name in f:
        uuid = get_cnt(dbconn, 'uuid')
        name = name.strip()
        if non_query(dbconn, '''insert into clans values (?,?)''', [uuid,name]) == 1:
            print 'imported clan %s with uuid %s' % (name, uuid)
    f.close()

def import_weapon_specials(dbconn, path):
    f = open( os.path.join(path, 'data'), 'rt' )
    for line in f:
        uuid = get_cnt(dbconn, 'uuid')
        tokens = line.split('"')
        if len(tokens) >= 2:
            tag    = tokens[0].strip()
            effect = tokens[1].strip()
            if non_query(dbconn, '''insert into effects values (?,?,?)''',
                        [uuid,tag,effect]):
                print 'imported effect %s with uuid %s' % (tag, uuid)
    f.close()


def import_armors(dbconn, path):
    f = open( os.path.join(path, 'data'), 'rt' )
    while True:
        if not f.readline().startswith('#'): break
        name    = value_or_null(f.readline())
        tn      = value_or_null(f.readline())
        rd      = value_or_null(f.readline())
        special = value_or_null(f.readline())
        cost    = value_or_null(f.readline())

        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into armors values(?,?,?,?,?,?)''',
                             [uuid,name,tn,rd,special,cost]):
            print 'imported armor %s with uuid %s' % (name, uuid)
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
    #print 'import %s skills' % categ
    print 'import skills from file %s' % path
    f = open( path, 'rt' )
    for line in f:
        tokens = line.split()
        if len(tokens) < 2:
            print 'ignoring line %s' % line
            continue
        name = tokens[0].replace('_', ' ')
        attrib = tokens[1]
        tags = tokens[2: len(tokens)]

        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into skills values(?,?,?,?)''',
                             [uuid,name,categ,attrib]):
            print 'imported skill %s with uuid %s, tags=%s' % (name, uuid, repr(tags))

            for t in tags:
                add_tag(dbconn, uuid, t)
        else:
            print 'cannot import skill %s' % name
    f.close()

def import_clan_school_skills(dbconn, clan, path):
    print 'import school skills from %s' % path

    f = open( path, 'rt' )
    while True:
        if not f.readline().startswith('#'): break
        s_name = f.readline().strip()
        skill_line = f.readline().strip()
        skills = skill_line.split(',')

        # get school uid
        print 'search uuid for school %s' % s_name
        s_uuid = query(dbconn, '''select uuid from schools where name=?''', [s_name])
        if s_uuid is not None and len(s_uuid) > 0:
            s_uuid = s_uuid[0][0]

        for s in skills:

            sk_name, sk_rank, sk_emph = parse_skill_line(s)
            if sk_name.startswith('*'):
                # add wildcard
                non_query(dbconn, '''insert into school_skills
                                     (school_uuid, skill_rank, wildcard)
                                     values(?,?,?)''',
                                  [s_uuid, 1, sk_name[1:]])
            else:
                # get skill uid
                print 'search uuid for skill %s' % s
                sk_uuid = query(dbconn, '''select uuid from skills where name=?''', [sk_name])
                if sk_uuid is not None and len(sk_uuid) > 0:
                    sk_uuid = sk_uuid[0][0]
                    non_query(dbconn, '''insert into school_skills
                                         (school_uuid, skill_uuid, skill_rank, emphases)
                                         values(?,?,?,?)''',
                                         [s_uuid, sk_uuid, sk_rank, sk_emph])
    f.close()

def import_categ_weapons(dbconn, categ, path):
    print 'import weapons from %s' % path

    f = open( path, 'rt' )
    sk_name = f.readline().strip()

    # get skill uid
    print 'search uuid for skill %s' % sk_name
    sk_uuid = query(dbconn, '''select uuid from skills where name=?''', [sk_name])
    if sk_uuid is not None and len(sk_uuid) > 0:
        sk_uuid = sk_uuid[0][0]

    while True:
        if not f.readline().startswith('#'): break
        name    = f.readline().strip()
        tags    = value_or_null(f.readline()).split(',')
        drs     = value_or_null(f.readline()).split(';')
        str_    = None
        min_str = None
        dr      = None
        dr_alt  = None
        range   = None
        special = None
        cost    = None
        if 'w' not in drs[0] and 'k' not in drs[0]:
            str_ = drs[0]
        elif 'k' in drs[0] or 'w' in drs[0]:
            dr = drs[0]
            if len(drs) > 1:
                dr_alt = drs[1]
        min_str  = value_or_null(f.readline())
        range    = value_or_null(f.readline())
        special  = value_or_null(f.readline())
        cost     = value_or_null(f.readline())

        if special is not None:
            # get special uid
            print 'search uuid for effect %s' % special
            special = query(dbconn, '''select uuid from effects where tag=?''', [special])
            if special is not None and len(special) > 0:
                special = special[0][0]
            else:
                special = None

        uuid = get_cnt(dbconn, 'uuid')
        if non_query(dbconn, '''insert into weapons
                                values(?,?,?,?,?,?,?,?,?,?)''',
                             [uuid,name,sk_uuid,dr,dr_alt,range,str_,
                             min_str, special, cost]):
            print 'imported weapon %s with uuid %s, tags=%s' % (name, uuid, repr(tags))

            for t in tags:
                add_tag(dbconn, uuid, t)
        else:
            print 'cannot import weapon %s' % name

    f.close()

def import_families(conn, path):
    for path, dirs, files in os.walk(path):
        dirn = os.path.basename(path)
        if dirn.startswith('.'):
            break
        for file_ in files:
            if file_.startswith('.') or file_.endswith('~'):
                continue
            import_clan_families(conn, file_, os.path.join(path, file_))

def import_schools(conn, path):
    for path, dirs, files in os.walk(path):
        dirn = os.path.basename(path)
        if dirn.startswith('.'):
            break
        for file_ in files:
            if file_.startswith('.') or file_.endswith('~'):
                continue
            import_clan_schools(conn, file_, os.path.join(path, file_))

def import_skills(conn, path):
    for path, dirs, files in os.walk(path):
        dirn = os.path.basename(path)
        if dirn.startswith('.'):
            break
        for file_ in files:
            if file_.startswith('.') or file_.endswith('~'):
                continue
            import_categ_skills(conn, file_.lower(), os.path.join(path, file_))

def import_school_skills(conn, path):
    for path, dirs, files in os.walk(path):
        dirn = os.path.basename(path)
        if dirn.startswith('.'):
            break
        for file_ in files:
            if file_.startswith('.') or file_.endswith('~'):
                continue
            import_clan_school_skills(conn, file_.lower(), os.path.join(path, file_))

def import_weapons(conn, path):
    for path, dirs, files in os.walk(path):
        dirn = os.path.basename(path)
        if dirn.startswith('.'):
            break
        for file_ in files:
            if file_.startswith('.') or file_.endswith('~'):
                continue
            import_categ_weapons(conn, file_.lower(), os.path.join(path, file_))

def importdb(conn, path):
    import_clans(conn, os.path.join(path, 'clans'))
    import_families(conn, os.path.join(path, 'families'))
    import_schools(conn, os.path.join(path, 'schools'))
    import_skills(conn, os.path.join(path, 'skills'))
    import_school_skills(conn, os.path.join(path, 'school_skills'))
    import_weapon_specials(conn, os.path.join(path, 'weapon_specials'))
    import_weapons(conn, os.path.join(path, 'weapons'))
    import_armors(conn, os.path.join(path, 'armors'))
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
            print 'insert db file: [share/l5rcm/l5rdb.sqlite]'
            path = raw_input()
            if len(path) == 0: path = 'share/l5rcm/l5rdb.sqlite'
            dbconn = connect(path)
        elif c == 'i':
            print 'insert import path: [./import/]'
            path = raw_input()
            if len(path) == 0: path = './import/'
            importdb(dbconn, path)
        elif c == '1':
            print 'insert db file: [share/l5rcm/l5rdb.sqlite]'
            path = raw_input()
            if len(path) == 0: path = 'share/l5rcm/l5rdb.sqlite'
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
