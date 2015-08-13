drop table if exists records;
create table records (
  id integer primary key autoincrement,
  latitude text not null,
  longitude text not null,
  timestamp integer not null
);
