# 查询用户权限
SELECT permission.*
FROM (((user
  INNER JOIN user_role ON user.id = user_role.user_id) INNER JOIN role ON user_role.role_id = role.id) INNER JOIN
  role_permission ON role.id = role_permission.role_id) INNER JOIN permission
    ON role_permission.permission_id = permission.id
WHERE user.id = 1;
