use runit;

create table users
(
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name varchar(50) not null,
  email varchar(100) not null,
  password varchar(500) not null,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
LOAD DATA LOCAL INFILE 'users.csv' INTO TABLE users FIELDS TERMINATED BY ','  ENCLOSED BY '"' LINES TERMINATED BY '\n' (name,email,password);
