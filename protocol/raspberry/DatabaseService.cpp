#include "DatabaseService.h"
#include <iostream>
#include <stdio.h>
#include <sqlite3.h>
#include <string>


using namespace std;





	DatabaseService::DatabaseService(const char *dbname){
		m_dbname = dbname;
	}


	ModeChauffe *DatabaseService::findModeChauffe(const char *requete){
		ModeChauffe *mode;

		sqlite3_stmt *stmt;
		int  rc = sqlite3_prepare_v2(m_db, requete, -1, &stmt, 0);
		if (rc == SQLITE_OK) {
			int nCols = sqlite3_column_count(stmt);
			if (nCols) {
				if (rc = sqlite3_step(stmt) == SQLITE_ROW){
					mode = new ModeChauffe();
					mode->m_cons = (float) sqlite3_column_double(stmt, 0);
					mode->m_max = (float) sqlite3_column_double(stmt, 1);
					mode->m_libelle = std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2)));
				}
			}
			sqlite3_finalize(stmt);
		}else{
			fprintf(stderr, "Error: %s\n", sqlite3_errmsg(m_db));
		}
		return mode;
	}


	ModeChauffe *DatabaseService::findModeChauffe(){

		ModeChauffe *mode;

		char *zErrMsg = 0;
		int rc;

		const char *requete1 = "SELECT m.cons, m.max, m.libelle FROM periode p join mode m on p.modeId = m.id \
							WHERE (p.dateDebut = date('now') and p.dateFin = date('now')) \
							and p.heureDebut <= time('now', 'localtime') and p.heureFin > time('now', 'localtime')";
		const char *requete2 = "SELECT m.cons, m.max, m.libelle FROM periode p join mode m on p.modeId = m.id \
							WHERE (p.dateDebut <= date('now') and p.dateFin > date('now')) \
							and p.heureDebut <= time('now', 'localtime') and p.heureFin > time('now', 'localtime')";
		const char *requete3 = "SELECT m.cons, m.max, m.libelle FROM periode p join mode m on p.modeId = m.id \
							WHERE p.jour = strftime('%w') \
							and p.heureDebut <= time('now', 'localtime') and p.heureFin > time('now', 'localtime');";


		rc = sqlite3_open(m_dbname, &m_db);
		if( rc ){
			fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(m_db));
			sqlite3_close(m_db);
			return NULL;
		}

		mode = findModeChauffe(requete1);
		if (not mode)
			mode = findModeChauffe(requete2);
		if (not mode)
			mode = findModeChauffe(requete3);

		sqlite3_close(m_db);

		return mode;
	}


	void DatabaseService::saveTemperature(float temperature){

		ModeChauffe *mode;


		char *zErrMsg = 0;
		int rc;


		const char *requete1 = "INSERT into  HISTO_TEMP('date','heure','temp') values(date('now', 'localtime'),time('now', 'localtime'),?)";

		rc = sqlite3_open(m_dbname, &m_db);
		if( rc ){
			fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(m_db));
			sqlite3_close(m_db);
			return;
		}

		sqlite3_stmt *stmt;
		rc = sqlite3_prepare_v2(m_db, requete1, -1, &stmt, 0);
		if (rc != SQLITE_OK){
			fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(m_db));
			sqlite3_close(m_db);
			return;
		}

		rc = sqlite3_bind_double(stmt, 1, temperature);
		if (rc != SQLITE_OK){
			fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(m_db));
			sqlite3_close(m_db);
			return;
		}

		rc = sqlite3_step(stmt);
		if (rc != SQLITE_DONE){
			fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(m_db));
			sqlite3_close(m_db);
			return;
		}



		sqlite3_close(m_db);

		return;
	}

