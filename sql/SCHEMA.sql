CREATE TABLE "accounts" (
	"login" VARCHAR NOT NULL,
	"password" VARCHAR NOT NULL
);
CREATE TABLE "histoTrameMcz" (
	"dateEnvoi" DATETIME, 
	"ordre" TEXT, 
	"puissance" TEXT, 
	"ventilation" TEXT, 
	"flagTrame" CHAR, 
	"typeOrdre" TEXT, 
	"message" TEXT);
	
CREATE TABLE "histo_temp" (
	"date" DATETIME, 
	"heure" DATETIME, 
	"temp" FLOAT);
	
CREATE TABLE "mode" (
	"id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , 
	"libelle" VARCHAR, 
	"cons" FLOAT, 
	"max" FLOAT);
	
CREATE TABLE "parametrage" (
	"code" VARCHAR PRIMARY KEY  NOT NULL , 
	"type" VARCHAR, "valeur" VARCHAR NOT NULL , 
	"commentaire" VARCHAR,
	"valeurs" VARCHAR);
	
CREATE TABLE "periode" (
	"id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , 
	"jour" VARCHAR, 
	"dateDebut" DATETIME, 
	"dateFin" DATETIME, 
	"heureDebut" DATETIME, 
	"heureFin" DATETIME, 
	"modeId" INTEGER);
	

