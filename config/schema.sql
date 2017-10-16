DROP DATABASE IF EXISTS scholar_tool_manager;
CREATE DATABASE scholar_tool_manager;
USE scholar_tool_manager;
GRANT SELECT, INSERT, UPDATE, DELETE ON scholar_tool_manager.* TO 'www-data'@'localhost'
IDENTIFIED BY 'www->R&daD6xZM6283n3-data';

CREATE TABLE user (
  `id`            INT(16)      NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(56)  NOT NULL,
  `email`         VARCHAR(56)  NOT NULL,
  `password`      VARCHAR(56)  NOT NULL,
  `name`          VARCHAR(56)  NOT NULL,
  `image`         VARCHAR(512) NOT NULL,
  `created_at`    REAL         NOT NULL,
  `last_login_at` REAL         NOT NULL,
  `available`     BOOL         NOT NULL,
  `total_usage`   INT(24)      NOT NULL,
  UNIQUE KEY `idx_email` (`email`),
  UNIQUE KEY `idx_username` (`username`),
  KEY `idx_created_at` (`created_at`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE role (
  `id`          INT(16)     NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(56) NOT NULL,
  `label`       VARCHAR(56) NOT NULL,
  `description` VARCHAR(512),
  UNIQUE KEY `idx_name` (`name`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;
INSERT INTO role VALUES (1, '超级管理员', 'root', '具备所有权限');
INSERT INTO role VALUES (2, '注册用户', 'user', '可登录');
INSERT INTO role VALUES (3, '小黑屋', 'ban', '禁止一切');

CREATE TABLE user_role (
  `id`      INT(16) NOT NULL AUTO_INCREMENT,
  `user_id` INT(16) NOT NULL,
  `role_id` INT(16) NOT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE permission (
  `id`          INT(16)     NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(56) NOT NULL,
  `label`       VARCHAR(56) NOT NULL,
  `description` VARCHAR(512),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;
INSERT INTO permission VALUES (1, '登录', 'login', '允许登录');
INSERT INTO permission VALUES (2, '后台管理', 'login', '允许进入后台管理');
INSERT INTO permission VALUES (3, '邀请码管理', 'manage_invitation_code', '允许进行邀请码管理');
INSERT INTO permission VALUES (4, '公告管理', 'manage_event', '允许进行公告管理');
INSERT INTO permission VALUES (5, '用户管理', 'manage_user', '允许进行用户管理');
INSERT INTO permission VALUES (6, '角色管理', 'manage_role', '允许进行用户角色管理');

CREATE TABLE role_permission (
  `id`            INT(16) NOT NULL AUTO_INCREMENT,
  `role_id`       INT(16) NOT NULL,
  `permission_id` INT(16) NOT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;
INSERT INTO role_permission VALUES (1, 1, 1);
INSERT INTO role_permission VALUES (2, 1, 2);
INSERT INTO role_permission VALUES (3, 1, 3);
INSERT INTO role_permission VALUES (4, 1, 4);
INSERT INTO role_permission VALUES (5, 1, 5);
INSERT INTO role_permission VALUES (6, 1, 6);
INSERT INTO role_permission VALUES (7, 2, 1);

CREATE TABLE invitation_code (
  `id`         INT(16)     NOT NULL AUTO_INCREMENT,
  `code`       VARCHAR(32) NOT NULL,
  `inviter_id` INT(16)     NOT NULL,
  `invitee_id` INT(16),
  `available`  BOOL        NOT NULL,
  `created_at` REAL        NOT NULL,
  `invited_at` REAL,
  UNIQUE KEY `idx_code` (`code`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE sessions (
  `id`         INT(16)      NOT NULL AUTO_INCREMENT,
  `session_id` VARCHAR(255) NOT NULL,
  `data`       BLOB,
  `expiry`     DATETIME,
  UNIQUE KEY `idx_session_id` (`session_id`),
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE event (
  `id`         INT(16)      NOT NULL  AUTO_INCREMENT,
  `user_id`    INT(16)      NOT NULL,
  `name`       VARCHAR(128) NOT NULL,
  `tag`        VARCHAR(128),
  `summary`    VARCHAR(512) NOT NULL,
  `content`    MEDIUMTEXT   NOT NULL,
  `created_at` REAL         NOT NULL,
  `available`  BOOL         NOT NULL,
  KEY `idx_created_at` (`created_at`),
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
CREATE TABLE sessions
  LIKE scholar_tool_manager.sessions;
CREATE TABLE event
  LIKE scholar_tool_manager.event;
