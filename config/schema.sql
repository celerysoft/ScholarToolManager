DROP DATABASE IF EXISTS scholar_tool_manager;
CREATE DATABASE scholar_tool_manager;
USE scholar_tool_manager;
GRANT SELECT, INSERT, UPDATE, DELETE ON scholar_tool_manager.* TO 'www-data'@'localhost'
IDENTIFIED BY 'www->R&daD6xZM6283n3-data';

CREATE TABLE user (
  `id`            INT(11)      NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(50)  NOT NULL,
  `email`         VARCHAR(50)  NOT NULL,
  `password`      VARCHAR(50)  NOT NULL,
  `name`          VARCHAR(50)  NOT NULL,
  `image`         VARCHAR(500) NOT NULL,
  `created_at`    REAL         NOT NULL,
  `last_login_at` REAL         NOT NULL,
  `available`     BOOL         NOT NULL,
  `total_usage`   INT(20)      NOT NULL,
  UNIQUE KEY `idx_email` (`email`),
  UNIQUE KEY `idx_username` (`username`),
  KEY `idx_created_at` (`created_at`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE role (
  `id`          INT(11)     NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(50) NOT NULL,
  `label`       VARCHAR(50) NOT NULL,
  `description` VARCHAR(500),
  UNIQUE KEY `idx_name` (`name`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;
INSERT INTO role VALUES (1, '超级管理员', 'root', '具备所有权限');
INSERT INTO role VALUES (2, '注册用户', 'user', '可登录');

CREATE TABLE user_role (
  `id`      INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `role_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE permission (
  `id`          INT(11)     NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(50) NOT NULL,
  `label`       VARCHAR(50) NOT NULL,
  `description` VARCHAR(500),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;
INSERT INTO permission VALUES (1, '登录', 'login', '允许登录');
INSERT INTO permission VALUES (2, '后台管理', 'login', '允许进入后台管理');
INSERT INTO permission VALUES (3, '权限管理', 'login', '允许进行权限管理');

CREATE TABLE role_permission (
  `id`            INT(11) NOT NULL AUTO_INCREMENT,
  `role_id`       INT(11) NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE invitation_code (
  `id`         INT(11)     NOT NULL AUTO_INCREMENT,
  `code`       VARCHAR(32) NOT NULL,
  `inviter_id` INT(11)     NOT NULL,
  `invitee_id` INT(11),
  `available`  BOOL        NOT NULL,
  `created_at` REAL        NOT NULL,
  `invited_at` REAL,
  UNIQUE KEY `idx_code` (`code`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE sessions (
  `id`         INT(11)      NOT NULL AUTO_INCREMENT,
  `session_id` VARCHAR(255) NOT NULL,
  `data`       BLOB,
  `expiry`     DATETIME,
  UNIQUE KEY `idx_session_id` (`session_id`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;


DROP DATABASE IF EXISTS scholar_tool_manager_test;
CREATE DATABASE scholar_tool_manager_test;
USE scholar_tool_manager_test;
GRANT SELECT, INSERT, UPDATE, DELETE ON scholar_tool_manager_test.* TO 'www-data'@'localhost';

CREATE TABLE user
  LIKE scholar_tool_manager.user;
CREATE TABLE role
  LIKE scholar_tool_manager.role;
CREATE TABLE user_role
  LIKE scholar_tool_manager.user_role;
CREATE TABLE permission
  LIKE scholar_tool_manager.permission;
CREATE TABLE role_permission
  LIKE scholar_tool_manager.role_permission;
CREATE TABLE invitation_code
  LIKE scholar_tool_manager.invitation_code;
