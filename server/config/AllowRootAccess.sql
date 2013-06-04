/* Create the database */
FLUSH PRIVILEGES;
UPDATE mysql.user SET Password=PASSWORD('elixys') WHERE user='root';
SET PASSWORD FOR root@'localhost' = '';
FLUSH PRIVILEGES;

