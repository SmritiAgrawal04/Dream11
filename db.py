from cassandra.cluster import Cluster
clstr=Cluster()

session=clstr.connect('userdb')
qry= '''
create table User (
   username text,
   password text,
   primary key(username)
);'''

session.execute(qry)


