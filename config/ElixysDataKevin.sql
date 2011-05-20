CREATE TABLE [sequences] (
[id] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
[seq_name] VARCHAR(50)  NOT NULL,
[seq_shortname] VARCHAR(20)  NOT NULL,
[seq_description] VARCHAR(250)  NULL
);

CREATE TABLE [unitoperations] (
[id] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
[unitop_name] VARCHAR(50)  NOT NULL,
[unitop_shortname] VARCHAR(20)  NOT NULL,
[unitop_sequence] INTEGER  NOT NULL,
[unitop_perams] VARCHAR(200)  NOT NULL
);

CREATE TABLE [users] (
[id] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
[user_password] VARCHAR(50)  NOT NULL,
[user_name] VARCHAR(50)  NOT NULL,
[user_last_ip] VARCHAR(15)  NOT NULL,
[user_access] NUMERIC DEFAULT '1' NOT NULL,
[user_last_access] TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
