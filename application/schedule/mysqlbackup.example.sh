#!/bin/bash

db_server='127.0.0.1'
db_user='dumper'
db_password='dumper->a7&alnMn-bb'
db_name='scholar_tool_manager'

# 备份时间
backup_date=`date +%Y%m%d`
# 备份日志路径
log_file_directory=/Users/admin/Documents/
# 备份日志文件名
log_file_name=database_backup.log
# 备份文件储存路径
backup_file_directory=/Users/admin/Documents/


echo "################## ${backup_date} #############################"
echo "开始备份"
# 日志记录头部
echo "" >> ${log_file_directory}${log_file_name}
echo "-------------------------------------------------" >> ${log_file_directory}${log_file_name}
echo "备份时间为 ${backup_date}，备份数据库 ${db_name} 开始" >> ${log_file_directory}${log_file_name}

# 正式备份数据库
mysqldump -h${db_server} -u${db_user} -p${db_password} ${db_name} > ${backup_file_directory}celerysoft-science-${backup_date}.sql 2>> ${log_file_directory}${log_file_name}

# 备份成功以下操作
if [ "$?" == 0 ];then
cd ${backup_file_directory}

# 为节约硬盘空间，将数据库压缩
#tar zcf ${table}${backup_date}.tar.gz ${backup_date}.sql > /dev/null
# 删除原始文件，只留压缩后文件
#rm -f ${backup_file_directory}/${backup_date}.sql
# 删除七天前备份，也就是只保存7天内的备份
#find ${backup_file_directory} -name "*.tar.gz" -type f -mtime +7 -exec rm -rf {} \; > /dev/null 2>&1

# 删除七天前的备份
find ${backup_file_directory} -name "*.sql" -type f -mtime +7 -exec rm -rf {} \; > /dev/null 2>&1

# 执行Python脚本将备份文件上传到七牛
echo "开始将备份文件上传至七牛" >> ${log_file_directory}${log_file_name}
cd /path/tp/venv
source ./bin/activate
cd /path/to/project
PYTHONPATH=/path/to/project/ /path/tp/venv/bin/python /path/to/project/application/schedule/backup_database.py >> ${log_file_directory}${log_file_name}
deactivate

echo "数据库 ${db_name} 备份成功!!" >> ${log_file_directory}${log_file_name}
else
# 备份失败则进行以下操作
echo "数据库 ${db_name} 备份失败!!" >> ${log_file_directory}${log_file_name}
fi

echo "完成备份"
echo "################## ${backup_date} #############################"
echo "-------------------------------------------------" >> ${log_file_directory}${log_file_name}