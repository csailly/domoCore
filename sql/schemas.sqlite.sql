BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `periode` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`jour`	VARCHAR,
	`dateDebut`	DATETIME,
	`dateFin`	DATETIME,
	`heureDebut`	DATETIME,
	`heureFin`	DATETIME,
	`modeId`	INTEGER
);
CREATE TABLE IF NOT EXISTS `parametrage` (
	`code`	VARCHAR NOT NULL,
	`type`	VARCHAR,
	`valeur`	VARCHAR NOT NULL,
	`commentaire`	VARCHAR,
	`valeurs`	VARCHAR,
	PRIMARY KEY(`code`)
);
CREATE TABLE IF NOT EXISTS `mode` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`libelle`	VARCHAR,
	`cons`	FLOAT,
	`max`	FLOAT
);
CREATE TABLE IF NOT EXISTS `histo_temp` (
	`date`	DATETIME,
	`heure`	DATETIME,
	`temp`	FLOAT,
	`sonde`	INTEGER
);
CREATE TABLE IF NOT EXISTS `histoTrameMcz` (
	`dateEnvoi`	DATETIME,
	`ordre`	TEXT,
	`puissance`	TEXT,
	`ventilation`	TEXT,
	`flagTrame`	CHAR,
	`typeOrdre`	TEXT,
	`message`	Text
);
CREATE TABLE IF NOT EXISTS `ACCOUNTS` (
	`login`	VARCHAR NOT NULL,
	`password`	VARCHAR NOT NULL
);
COMMIT;
