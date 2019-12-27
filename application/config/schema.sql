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
    `status`       TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废，3 - 已使用',
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
    `id`                 INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`               VARCHAR(36)    NOT NULL,
    `type`               INT(4)         NOT NULL
        COMMENT '套餐类型：0 - 包月套餐，1 - 流量套餐',
    `title`              VARCHAR(64)    NOT NULL
        COMMENT '套餐名',
    `subtitle`           VARCHAR(64)    NOT NULL
        COMMENT '副标题',
    `description`        TEXT           NOT NULL
        COMMENT '套餐描述',
    `package`            BIGINT(20)     NOT NULL
        COMMENT '流量',
    `price`              DECIMAL(12, 2) NOT NULL
        COMMENT '价格',
    `initialization_fee` DECIMAL(12, 2) NOT NULL
        COMMENT '初装费',
    `created_at`         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`             TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废，3 - 下架',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '学术服务模板';

CREATE TABLE scholar_payment_account
(
    `id`         INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`       VARCHAR(36)    NOT NULL,
    `user_uuid`  VARCHAR(36)    NOT NULL COMMENT '账户持有人UUID',
    `balance`    DECIMAL(12, 2) NOT NULL DEFAULT 0 COMMENT '账户余额',
    `created_at` DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`     TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '学术积分账户';

CREATE TABLE scholar_payment_account_log
(
    `id`             INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`           VARCHAR(36)    NOT NULL,
    `account_uuid`   VARCHAR(36)    NOT NULL COMMENT '学术积分账户UUID',
    `former_balance` DECIMAL(12, 2) NOT NULL COMMENT '操作前账户余额',
    `amount`         DECIMAL(12, 2) NOT NULL COMMENT '金额',
    `balance`        DECIMAL(12, 2) NOT NULL COMMENT '操作后账户余额',
    `type`           TINYINT        NOT NULL COMMENT '0 - 减少，1 - 增加',
    `purpose_type`   TINYINT        NOT NULL COMMENT '0 - 消费(-)，1 - 充值(+)，2 - 转出(-)，3 - 转入(+)，4 - 补缴(-)，5 - 补偿(+)',
    `created_at`     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`         TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '学术积分账户流水';

CREATE TABLE trade_order
(
    `id`          INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`        VARCHAR(36)    NOT NULL,
    `user_uuid`   VARCHAR(36)    NOT NULL COMMENT '交易方UUID',
    `type`        TINYINT        NOT NULL COMMENT '0 - 退款，1 - 充值，2 - 消费，3 - 转账，4 - 提现',
    `amount`      DECIMAL(12, 2) NOT NULL COMMENT '金额',
    `description` TEXT COMMENT '交易描述',
    `created_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`      TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 支付完成，2 - 作废，3 - 支付中，4 - 部分支付，5 - 退款中，6 - 部分退款，7 - 全部退款，8 - 取消',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '交易订单';

CREATE TABLE subscribe_service_snapshot
(
    `id`                    INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`                  VARCHAR(36)    NOT NULL,
    `trade_order_uuid`      VARCHAR(36)    NOT NULL COMMENT '交易订单UUID',
    `user_uuid`             VARCHAR(36)    NOT NULL COMMENT '订购人UUID',
    `service_password`      VARCHAR(64)    NOT NULL COMMENT '服务密码',
    `auto_renew`            TINYINT        NOT NULL DEFAULT 0 COMMENT '是否自动续费：0 - 否，1 - 是',
    `service_template_uuid` VARCHAR(36)    NOT NULL COMMENT '服务模板UUID',
    `type`                  INT(4)         NOT NULL
        COMMENT '套餐类型：0 - 包月套餐，1 - 流量套餐',
    `title`                 VARCHAR(64)    NOT NULL
        COMMENT '套餐名',
    `subtitle`              VARCHAR(64)    NOT NULL
        COMMENT '副标题',
    `description`           TEXT           NOT NULL
        COMMENT '套餐描述',
    `package`               BIGINT(20)     NOT NULL
        COMMENT '流量',
    `price`                 DECIMAL(12, 2) NOT NULL
        COMMENT '价格',
    `initialization_fee`    DECIMAL(12, 2) NOT NULL
        COMMENT '初装费',
    `created_at`            DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`            DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`                TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '订购学术服务交易快照';

CREATE TABLE payment_method
(
    `id`         INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`       VARCHAR(36) NOT NULL,
    `name`       VARCHAR(32) NOT NULL COMMENT '渠道名',
    `created_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`     TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '支付渠道';

CREATE TABLE pay_order
(
    `id`                   INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`                 VARCHAR(36)    NOT NULL,
    `type`                 TINYINT        NOT NULL COMMENT '1 - 充值，2 - 消费，3 - 转账，4 - 提现',
    `amount`               DECIMAL(12, 2) NOT NULL COMMENT '付款金额',
    `trade_order_uuid`     VARCHAR(36)    NOT NULL COMMENT '交易订单UUID',
    `payment_method_uuid`  VARCHAR(36)    NOT NULL COMMENT '交易渠道UUID',
    `payment_method_token` VARCHAR(64)    NOT NULL COMMENT '交易渠道唯一标识符',
    `created_at`           DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`           DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`               TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 支付完成，2 - 作废，3 - 支付中',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '付款订单';

CREATE TABLE refund_order
(
    `id`                   INT(11)        NOT NULL AUTO_INCREMENT,
    `uuid`                 VARCHAR(36)    NOT NULL,
    `type`                 TINYINT        NOT NULL COMMENT '0 - 非原路退款，1 - 原路退款',
    `amount`               DECIMAL(12, 2) NOT NULL COMMENT '退款金额',
    `trade_order_uuid`     VARCHAR(36)    NOT NULL COMMENT '交易订单UUID',
    `payment_method_uuid`  VARCHAR(36)    NOT NULL COMMENT '交易渠道UUID',
    `payment_method_token` VARCHAR(64)    NOT NULL COMMENT '交易渠道唯一标识符',
    `created_at`           DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`           DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`               TINYINT(4)     NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 退款完成，2 - 作废，3 - 退款中',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '退款订单';

/*
CREATE TABLE table_name
(
    `id`                 INT(11)     NOT NULL AUTO_INCREMENT,
    `uuid`               VARCHAR(36) NOT NULL,
    `created_at`         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status`             TINYINT(4)  NOT NULL DEFAULT 1 COMMENT '状态：0 - 初始化，1 - 有效，2 - 作废',
    PRIMARY KEY (`id`)
)
    ENGINE = innodb
    DEFAULT CHARSET = utf8
    COMMENT = '';
*/