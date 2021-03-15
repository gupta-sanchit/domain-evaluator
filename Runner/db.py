import json

import pymongo

client = pymongo.MongoClient("localhost", 27017)

db = client.test

d = db.domainCluster

with open('../domainsDB.json', 'r') as fp:
    da = json.load(fp)

# da['domain'].append('a')
# da['domain'].append('b')
# da['domain'].append('c')
# da['domain'].append('d')
# da['domain'].append('e')
# da['domain'].append('f')

# d.insert_one(da)
x = 'b'
d.update_one({"id": "domain-data"}, {'$push': {"domain": x}})
