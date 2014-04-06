#include <iostream>
#include "DatabaseService.h"
#include "TempService.h"

using namespace std;

int main (int argc, char** argv) {

DatabaseService dbService("/home/pi/syno/domotique.sqlite");

TempService tempService;

ModeChauffe *currentModeChauffe = dbService.findModeChauffe();
float currentTemp = tempService.getTemp();
//db.saveTemperature(currentTemp);

if (currentModeChauffe){
	cout << "Mode " << currentModeChauffe->m_libelle << " - Cons : " << currentModeChauffe->m_cons << " - Max : " << currentModeChauffe->m_max << endl;
	cout << currentTemp << endl;
}

return 0;
}
