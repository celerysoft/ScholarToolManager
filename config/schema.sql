DROP DATABASE IF EXISTS scholar_tool_manager;
CREATE DATABASE scholar_tool_manager;
USE scholar_tool_manager;
GRANT SELECT, INSERT, UPDATE, DELETE ON scholar_tool_manager.* TO 'www-data'@'localhost'
IDENTIFIED BY 'www->R&daD6xZM6283n3-data';

CREATE TABLE user (
  `id`            INT(16)      NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(64)  NOT NULL,
  `email`         VARCHAR(64)  NOT NULL,
  `password`      VARCHAR(64)  NOT NULL,
  `name`          VARCHAR(64)  NOT NULL,
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
  `name`        VARCHAR(64) NOT NULL,
  `label`       VARCHAR(64) NOT NULL,
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
  `name`        VARCHAR(64) NOT NULL,
  `label`       VARCHAR(64) NOT NULL,
  `description` VARCHAR(512),
  UNIQUE KEY `idx_name` (`name`),
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
INSERT INTO permission VALUES (7, '套餐模版管理', 'manage_service_template', '允许进行套餐模版管理');
INSERT INTO permission VALUES (8, '学术积分管理', 'manage_scholar_balance', '允许进行学术积分管理');
INSERT INTO permission VALUES (9, '套餐管理', 'manage_service', '允许进行套餐管理');

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
INSERT INTO role_permission VALUES (8, 1, 7);
INSERT INTO role_permission VALUES (9, 1, 8);
INSERT INTO role_permission VALUES (10, 1, 9);
INSERT INTO role_permission VALUES (11, 2, 9);

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

CREATE TABLE user_service (
  `id`         INT(16) NOT NULL  AUTO_INCREMENT,
  `user_id`    INT(16) NOT NULL,
  `service_id` INT(16) NOT NULL,
  `service_type` INT(11)   NOT NULL COMMENT '0 - monthly, 1 - data',
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE service (
  `id`            INT(16) NOT NULL  AUTO_INCREMENT,
  `template_id`   INT(16) NOT NULL COMMENT '套餐模版id',
  `type`          INT(11) NOT NULL COMMENT '0 - 包月套餐，1 - 流量套餐',
  `usage`         BIGINT(16) NOT NULL COMMENT '已用流量',
  `package`       BIGINT(16) NOT NULL COMMENT '总流量',
  `reset_at`      datetime COMMENT '重置流量时间点，包月套餐专用字段',
  `last_reset_at` datetime COMMENT '上次重置流量的时间点',
  `created_at`    datetime    NOT NULL COMMENT '创建于',
  `expired_at`    datetime    NOT NULL COMMENT '过期于',
  `total_usage`   BIGINT(16) NOT NULL COMMENT '已使用流量合计',
  `auto_renew`    BOOL COMMENT '自动续费，包月套餐专用字段',
  `available`     BOOL    NOT NULL COMMENT '是否有效',
  `alive`         BOOL    NOT NULL COMMENT '是否存在，不存在即被释放，无法续费',
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE service_password (
  `id`         INT(16)     NOT NULL  AUTO_INCREMENT,
  `service_id` INT(16)     NOT NULL,
  `service_type` INT(11)   NOT NULL COMMENT '0 - monthly, 1 - data',
  `port`       INT(6)      NOT NULL COMMENT '端口',
  `password`   VARCHAR(64) NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE service_template (
  `id`                 INT(16)      NOT NULL  AUTO_INCREMENT,
  `type`               INT(4)       NOT NULL COMMENT '套餐类型，1-流量，0-包月',
  `title`              VARCHAR(64)  NOT NULL COMMENT '套餐名',
  `subtitle`           VARCHAR(64)  NOT NULL COMMENT '副标题',
  `description`        VARCHAR(512) NOT NULL COMMENT '套餐描述',
  `balance`            BIGINT(16)      NOT NULL COMMENT '流量',
  `price`              INT(16)      NOT NULL COMMENT '价格',
  `initialization_fee` INT(16)      NOT NULL COMMENT '初装费',
  `available`     BOOL    NOT NULL,
  PRIMARY KEY (`id`)
)
  ENGINE = innodb
  DEFAULT CHARSET = utf8;

CREATE TABLE user_scholar_balance (
  `id`      INT(16) NOT NULL  AUTO_INCREMENT,
  `user_id` INT(16) NOT NULL,
  `balance` INT(16) NOT NULL COMMENT '学术积分',
  UNIQUE KEY `idx_user_id` (`user_id`),
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
CREATE TABLE user_service
  LIKE scholar_tool_manager.user_service;
CREATE TABLE service
  LIKE scholar_tool_manager.service;
CREATE TABLE service_password
  LIKE scholar_tool_manager.service_password;
CREATE TABLE service_template
  LIKE scholar_tool_manager.service_template;
CREATE TABLE user_scholar_balance
  LIKE scholar_tool_manager.user_scholar_balance;
