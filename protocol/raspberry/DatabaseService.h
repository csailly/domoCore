#ifndef DEF_DATABASE_SERVICE
#define DEF_DATABASE_SERVICE

#include <sqlite3.h>
#include <string>

//Classe repr�sentant un mode de chauffe
//avec une temp�rature de consigne et une temp�rature maximale
// au del� de laquelle le chauffage doit stopper
class ModeChauffe {
	public:
	//Temp�rature de consigne
	float m_cons;
	//Temp�rature maximale
	float m_max;
	//Libell�
	std::string m_libelle;
};

//Classe de Services d'acc�s au donn�es
class DatabaseService {
	public :
	//Constructeur
	DatabaseService(const char *dbname);
	//Permet de rechercher le mode de chauffe en cours
	ModeChauffe *findModeChauffe();
	//Permet de sauvegarder la temp�rature en base
	void saveTemperature(float temperature);

	private :
	//Nom du fichier de la base sqlite
	const char *m_dbname;
	//Pointeur sur la base de donn�es
	sqlite3 *m_db;
	
	//M�thode permettant de rechercher un mode de chauffe � partir d'une requ�te
	ModeChauffe *findModeChauffe(const char *requete);
	
};

#endif