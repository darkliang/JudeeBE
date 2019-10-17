# 后端与数据库部署

## Docker部署
非专业用户不推荐使用Docker单独部署
修改Dockerfile中的ENV为你的数据库地址和密码等
```
docker build -t lpojbackend .
docker run -d -p 8000:8000 lpojbackend
```

## 一般部署

1. 首先安装Django
```
pip install django

pip install djangorestframework

pip install django-filter

sudo apt-get install python-django

pip install django-cors-headers

pip install mysqlclient
```
2. 安装数据库，已安装的可跳过
```
sudo apt-get install mysql-server 

mysql -uroot -p
mysql > CREATE DATABASE LPOJ DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
mysql > USE mysql
mysql > GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'  IDENTIFIED BY 'your_password'  WITH GRANT OPTION;
mysql > ALTER user 'root'@'%' IDENTIFIED WITH mysql_native_password by 'your_password';
mysql > flush privileges;

sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf 

#修改bind-address 为 0.0.0.0
```
3. 部署后端
```
cd Backend

cd Backend

sudo nano setting.py
# 修改数据库配置为你自己的数据库IP和用户名密码

cd ..

python manage.py makemigrations

python manage.py migrate

echo "from django.contrib.auth.models import User; User.objects.filter(email=\"admin@example.com\").delete(); User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin\")" | python manage.py shell

python manage.py runserver 0.0.0.0:8000
```
4. 安装sftp服务（不安装无法判题,一般云服务器会自动安装）
```
sudo apt-get install openssh-server
sftp yourusername@localhost # 验证是否安装成功！
```
5. 添加管理员
> 安装成功后，先通过IP:80访问OJ，注册一个用户
> 
> 然后进入 IP:8000/admin 以用户名admin 密码admin 登录后台（请及时修改后台密码）
> 
> 修改User表中，你注册的超级用户的type为3，使得你注册的用户变为超级管理员