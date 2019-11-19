# 查询用户权限
SELECT permission.*
FROM (((user
  INNER JOIN user_role ON user.id = user_role.user_id) INNER JOIN role ON user_role.role_id = role.id) INNER JOIN
  role_permission ON role.id = role_permission.role_id) INNER JOIN permission
    ON role_permission.permission_id = permission.id
WHERE user.id = 1;

# 查询有效Service
SELECT service_password.* FROM service INNER JOIN service_password ON service.id = service_password.service_id WHERE service.alive = TRUE and service.available = TRUE;

# 查询用户的Service
select
       service.id,
       service_password.port,
       service_password.password,
       service.package,
       service.`usage`,
       service.last_usage,
       service.total_usage,
       service.available,
       user.username,
       user.email
from service
left join service_password on service_password.service_id = service.id
left join user_service on user_service.service_id = service.id
left join user on user.id = user_service.user_id
where user.username = '';