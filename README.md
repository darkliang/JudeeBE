# 后端开发环境配置

## 一般配置

1. clone项目到本地

2. 安装Django相关环境

   ```
   pip install django
   
   pip install djangorestframework
   
   pip install django-filter
   
   pip install psycopg2
   
   pip install djangorestframework-stubs
   
   pip install django-cors-headers
   ```

   

3. 修改`/JudeeBE/settings.py`，配置数据库HOST为`10.20.1.255`

4. 管理员账户为`admin`       `ljh123456`

## （optional）使用服务器的interpreter

使用服务器的interpreter（解释器），则不需要第2步。以下为`Pycharm`配置步骤

1. 在File->Settings->Project->Project interpreter, add一个新的interpreter
2. 选择SSH Interpreter->New server configuration, 输入用户名密码
3. 选择interpreter路径，一般在 `/home/1171xxxx_cs308/anaconda3/envs/cs309/bin/python3.7` 
4. （optional）选择 `mapping` 路径，会将本地的项目实时同步到远程服务器上

