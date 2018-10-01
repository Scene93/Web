CREATE TABLE users(name varchar(20), password varchar(255), e_mail varchar(20), hp varchar(20));
CREATE TABLE board(idx integer PRIMARY KEY, title varchar(20), writer varchar(20), date_time varchar(20), data varchar(255), filename varchar(255));
CREATE TABLE comments(idx integer PRIMARY KEY, data varchar(20), writer varchar(20), date_time varchar(20), post_num integer);
