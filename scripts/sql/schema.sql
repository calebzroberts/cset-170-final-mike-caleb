create database bankdb;

use bankdb;

create table people (
	username varchar(32) primary key,
    password varchar(64) not null,
    first_name varchar(32) not null,
    last_name varchar(64) not null
);

create table roles (
	username varchar(32) primary key,
    is_admin boolean default FALSE,
    constraint fk_roles_people foreign key (username) references people (username)
);

create table users (
	ssn varchar(64) primary key,
    username varchar (32) unique not null,
    address varchar(256) not null,
    phone varchar(16) not null,
    approved boolean default FALSE,
	constraint fk_users_people foreign key (username) references people (username),
    constraint fk_users_roles foreign key (username) references roles (username)
);

create table accounts (
	acct_num int primary key,
    ssn varchar(64) unique not null,
    balance decimal(18, 2),
    constraint fk_accounts_users foreign key (ssn) references users (ssn)
);

SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'docs/supp/people.txt'
INTO TABLE people
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'docs/supp/roles.txt'
INTO TABLE roles
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(username, @is_admin_text)
SET is_admin = CASE
    WHEN UPPER(REPLACE(@is_admin_text, '\r', '')) = 'TRUE' THEN 1
    WHEN UPPER(REPLACE(@is_admin_text, '\r', '')) = 'FALSE' THEN 0
    ELSE NULL
END;

LOAD DATA LOCAL INFILE 'docs/supp/users.txt'
INTO TABLE users
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(ssn, username, address, phone, @approved_text)
SET approved = CASE
    WHEN UPPER(REPLACE(@approved_text, '\r', '')) = 'TRUE' THEN 1
    WHEN UPPER(REPLACE(@approved_text, '\r', '')) = 'FALSE' THEN 0
    ELSE NULL
END;

LOAD DATA LOCAL INFILE 'docs/supp/accounts.txt'
INTO TABLE accounts
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;