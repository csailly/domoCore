#ifndef DEF_DATABASE_SERVICE
#define DEF_DATABASE_SERVICE

#include <sqlite3.h>
#include <string>

//Classe représentant un mode de chauffe
//avec une température de consigne et une température maximale
// au delà de laquelle le chauffage doit stopper
class ModeChauffe {
	public:
	//Température de consigne
	float m_cons;
	//Température maximale
	float m_max;
	//Libellé
	std::string m_libelle;
};

//Classe de Services d'accès au données
class DatabaseService {
	public :
	//Constructeur
	DatabaseService(const char *dbname);
	//Permet de rechercher le mode de chauffe en cours
	ModeChauffe *findModeChauffe();
	//Permet de sauvegarder la température en base
	void saveTemperature(float temperature);

	private :
	//Nom du fichier de la base sqlite
	const char *m_dbname;
	//Pointeur sur la base de données
	sqlite3 *m_db;
	
	//Méthode permettant de rechercher un mode de chauffe à partir d'une requête
	ModeChauffe *findModeChauffe(const char *requete);
	
};

#endif