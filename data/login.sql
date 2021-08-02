CREATE DATABASE loginData;
use loginData;

Create Table IF NOT EXISTS accounts (
  'id' int(11) Not Null AUTO_INCREMENT,
  'username' varchar(50) NOT NULL,
  'password' varchar(255) NOT NULL,
  'email' varchar(100) NOT NULL,
  PRIMARY KEY ('id')
  ) Engine=InnoDB AUTO_INCREMENT=2 Default CHARSET=utf8;