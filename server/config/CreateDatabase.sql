/* Create the database */

/* Drop any existing database to allow this file to be reimported as needed */
DROP DATABASE IF EXISTS Elixys;

/* Create the database */
CREATE DATABASE Elixys;

/* Grant usage */
GRANT USAGE ON *.* TO Apache@'localhost' IDENTIFIED BY 'devel';
GRANT USAGE ON *.* TO Elixys@'localhost' IDENTIFIED BY 'devel';

/* Grant privileges */
GRANT ALL PRIVILEGES ON Elixys.* TO Apache@'localhost' IDENTIFIED BY 'devel';
GRANT ALL PRIVILEGES ON Elixys.* TO Elixys@'localhost' IDENTIFIED BY 'devel';
FLUSH PRIVILEGES;

