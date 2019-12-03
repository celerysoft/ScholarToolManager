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
    `id`          INT(11)      NOT NULL AUTO_INCREMENT,
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

CREATE TABLE service
(
    `id`            INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`          VARCHAR(36) NOT NULL,
    `user_uuid`     VARCHAR(36) NOT NULL COMMENT '所属用户UUID',
    `template_uuid` VARCHAR(36) NOT NULL COMMENT '学术服务模板UUID',
    `type`          TINYINT(4)  NOT NULL
        COMMENT '0 - 包月套餐，1 - 流量套餐',
    `usage`         BIGINT(16)  NOT NULL
        COMMENT '已用流量',
    `package`       BIGINT(16)  NOT NULL
        COMMENT '总流量',
    `auto_renew`    TINYINT(4) COMMENT '自动续费状态：0 - 不自动，1 - 自动续费，包月套餐专用字段',
    `reset_at`      DATETIME COMMENT '下次将已用流量重置为0的时间点，包月套餐专用字段',
    `last_reset_at` DATETIME COMMENT '上次将已用流量重置为0的时间点，暨上次续费的时间',
    `expired_at`    DATETIME COMMENT '套餐过期时间，流量套餐专用字段',
    `total_usage`   BIGINT(16)  NOT NULL COMMENT '已使用流量合计',
    `port`          INT(11)     NOT NULL COMMENT '服务绑定的端口号',
    `password`      VARCHAR(64) NOT NULL COMMENT '服务密码',
    `created_at`    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`        TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废，3 - 暂停，待续费，4 - 失效',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '学术服务';

CREATE TABLE service_template
(
    `id`                 INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`               VARCHAR(36) NOT NULL,
    `type`               INT(4)      NOT NULL
        COMMENT '套餐类型：0 - 包月套餐，1 - 流量套餐',
    `title`              VARCHAR(64) NOT NULL
        COMMENT '套餐名',
    `subtitle`           VARCHAR(64) NOT NULL
        COMMENT '副标题',
    `description`        TEXT        NOT NULL
        COMMENT '套餐描述',
    `package`            BIGINT(20)  NOT NULL
        COMMENT '流量',
    `price`              INT(11)     NOT NULL
        COMMENT '价格',
    `initialization_fee` INT(11)     NOT NULL
        COMMENT '初装费',
    `created_at`         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`             TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '学术服务模板';