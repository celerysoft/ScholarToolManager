DROP DATABASE IF EXISTS scholar_tool;
CREATE DATABASE scholar_tool DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
USE scholar_tool;

GRANT SELECT, INSERT, UPDATE, DELETE ON scholar_tool.* TO 'www-data'@'localhost'
    IDENTIFIED BY 'www->R&daD6xZM6283n3-data';

GRANT SELECT, SHOW VIEW, LOCK TABLES, TRIGGER on scholar_tool.* TO 'dumper'@'localhost'
    IDENTIFIED BY 'dumper->a7&alnMn-bb';

CREATE TABLE user
(
    `id`         INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`       VARCHAR(36) NOT NULL,
    `username`   VARCHAR(64) NOT NULL,
    `email`      VARCHAR(64) NOT NULL,
    `password`   VARCHAR(64) NOT NULL,
    `created_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`     TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '用户';

CREATE TABLE invitation_code
(
    `id`           INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`         VARCHAR(36) NOT NULL,
    `code`         VARCHAR(36) NOT NULL,
    `inviter_uuid` VARCHAR(36) NOT NULL,
    `invitee_uuid` VARCHAR(36)          DEFAULT NULL,
    `invited_at`   DATETIME             DEFAULT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_at`   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`       TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '邀请码';

CREATE TABLE event
(
    `id`          INT(16)      NOT NULL AUTO_INCREMENT,
    `uuid`        VARCHAR(36)  NOT NULL,
    `author_uuid` VARCHAR(36)  NOT NULL,
    `title`       VARCHAR(128) NOT NULL,
    `summary`     VARCHAR(512) NOT NULL,
    `content`     MEDIUMTEXT   NOT NULL,
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`      TINYINT(4)   NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '公告';