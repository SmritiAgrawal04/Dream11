from cassandra.cluster import Cluster
clstr=Cluster()

session=clstr.connect()

#Drop Keyspaces 
keyspace = ['playermapping','userdb','userscore']

for key in keyspace:
    qry = 'drop KEYSPACE '+key+' ;'
    session.execute(qry)