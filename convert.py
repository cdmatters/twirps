import json
import sqlite3
import sys

def generate_d3_json():
    with open('map.json', 'r+') as f:
        twirp_map = json.load(f)

    converter = {}
    nodes = []
    edges = []

    parldb = '/Users/macintosh/Programming/Projects/Parliament/parl.db'

    with sqlite3.connect(parldb) as conn:
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT Party FROM MPCommons')
        party_keys = {party[0]:i for i, party in enumerate(cur.fetchall())}
        party_keys.update({'error':19})

        for i, mp in enumerate(twirp_map):
            url = 'https://twitter.com/%s'%mp
                # conn.execute('SELECT MPCommons.Constituency, MPCommons.Party FROM MPCommons INNER JOIN Addresses\
                #     ON MPCommons.OfficialId=Addresses.OfficialId WHERE Addresses.Address=?',(url,))
            cur.execute('SELECT OfficialId FROM Addresses WHERE Address=?',(url,))
            official_id =  cur.fetchall()
            bonus_data = [['error', 'error', 'error']]

            if len(official_id)>0:
                cur.execute('SELECT Name, Constituency, Party  FROM MPCommons WHERE OfficialId=?', official_id[0])
                bonus_data = cur.fetchall()



            node_data = {'name': bonus_data[0][0], 'constituency':bonus_data[0][1],
                        'party':bonus_data[0][2], 'handle':mp, 'party_no':party_keys[bonus_data[0][2]], 'ego':5}

            converter.update({mp:i})
            nodes.append(node_data)
    
    for i, from_mp in enumerate(twirp_map):
        for key in ['retweets', 'mentions']:
            for to_mp in twirp_map[from_mp][key]:
                edge_data = {'source':i,
                            'target':converter[to_mp],
                            'value': twirp_map[from_mp][key][to_mp],
                            'contact': key}
                if edge_data['source']!=edge_data['target'] and edge_data['value']> 10:
                    edges.append(edge_data)


    result = {'nodes':nodes, 'links':edges, 'old':twirp_map}

    with open('map_d3.json', 'w') as f:
        f.write(json.dumps(result))



def commands():
    if len(sys.argv)<2:
        print 'more args necc'
    elif sys.argv[1]=='d3_map':
        generate_d3_json()
    else:
        print 'bad args'

if __name__ == '__main__':
    commands()