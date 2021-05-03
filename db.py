from cassandra.cluster import Cluster
clstr=Cluster()

# user database
session=clstr.connect()
session.execute("create keyspace userdb with replication={'class': 'SimpleStrategy', 'replication_factor' : 3};")

session=clstr.connect('userdb')
qry= '''
create table User (
   username text,
   password text,
   primary key(username)
);'''
session.execute(qry)


# user score corresponding to each match
session=clstr.connect()
session.execute("create keyspace userscore with replication={'class': 'SimpleStrategy', 'replication_factor' : 3};")

session=clstr.connect('userscore')
qry= '''
create table Ashes (
   username text,
   score int,
   primary key(username)
);'''
session.execute(qry)

qry= '''
create table Wisden (
   username text,
   score int,
   primary key(username)
);'''
session.execute(qry)

qry= '''
create table Pataudi (
   username text,
   score int,
   primary key(username)
);'''
session.execute(qry)



# player-user mapping corresponding to each match
session=clstr.connect()
session.execute("create keyspace playermapping with replication={'class': 'SimpleStrategy', 'replication_factor' : 3};")

session=clstr.connect('playermapping')
qry= '''
create table Ashes (
   player text,
   usernames text,
   score int,
   primary key(player)
);'''
session.execute(qry)

qry= '''
create table Wisden (
   player text,
   usernames text,
   score int,
   primary key(player)
);'''
session.execute(qry)

qry= '''
create table Pataudi (
   player text,
   usernames text,
   score int,
   primary key(player)
);'''
session.execute(qry)


