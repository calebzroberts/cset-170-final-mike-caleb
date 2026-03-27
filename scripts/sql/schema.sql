create database mncbank;

use mncbank;

create table people (
	username varchar(32) primary key,
    password varchar(64) not null),
    first_name varchar(32) not null,
    last_name varchar(64) not null;
    
create table roles (
	username varchar(32) primary key,
    is_admin boolean default FALSE,
    constraint fk_roles_people foreign key (username) references people (username)
);

create table users (
	ssn varchar(64) primary key,
    username varchar (32) unique not null,
    address varchar(256) not null,
    phone int not null,
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
    