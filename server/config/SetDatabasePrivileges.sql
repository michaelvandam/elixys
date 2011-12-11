/* Create the database */

/* Grant usage */
GRANT USAGE ON *.* TO Apache@'localhost' IDENTIFIED BY 'devel';
GRANT USAGE ON *.* TO Elixys@'localhost' IDENTIFIED BY 'devel';

/* Grant privileges */
GRANT ALL PRIVILEGES ON Elixys.* TO Apache@'localhost' IDENTIFIED BY 'devel';
GRANT ALL PRIVILEGES ON Elixys.* TO Elixys@'localhost' IDENTIFIED BY 'devel';
FLUSH PRIVILEGES;

