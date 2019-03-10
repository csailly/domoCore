#include <wiringPi.h>
#include <iostream>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <stdlib.h>
#include <sched.h>
#include <sstream>
#include <string.h>

/*
Licence : CC by sa


g++ emetteurMCZ.cpp  -o emetteurMCZ -lwiringPi

sudo ./emetteur <txPin> <commande> <puissance> <ventilation>

<commande> -> 2 = on, 0 = off, 4 = auto
<puissance> -> puissance de chauffe de 1 à 5
<ventilation> -> ventilation de 1 à 6. 6 = auto.

sudo ./emetteur 0 0 2 6

*/

using namespace std;


//Durée fronts
int dureeFront = 390;
//Durée entre 2 données
int dureeInterDonnees = 860;
//Durée entre 2 messages
int dureeInterMessage = 5080;
//Nombre d'envois du message
int nbEnvois = 5;


unsigned long emetteurCode1=0x97d;
unsigned long emetteurCode2=0x999;
unsigned long emetteurCode3=0x813;
unsigned long code1=0xca9;
unsigned long code2=0xaeb;
//code1	code2
//0xca9	0xaeb
//0x8ab	0xeab
//0x829	0xf21
//0xc2b	0xb61

int txPin;						// N° du pin utilisé pour l'envoi des données

bool bit2Message[7][12]={};

bool* bit2EmetteurCode1=NULL;		// 12 bits Identifiant partie 1 émetteur
bool* bit2EmetteurCode2=NULL;		// 12 bits Identifiant partie 2 émetteur
bool* bit2EmetteurCode3=NULL;		// 12 bits Identifiant partie 3 émetteur
bool* bit2Donnee1=NULL;			// 12 bits Donnée 1
bool* bit2Code1=NULL;				// 12 bits Code 1
bool* bit2Donnee2=NULL;			// 12 bits Donnée 2
bool* bit2Code2=NULL;				// 12 bits Code 2

bool bit2Puissance[3] = {};			// 3 bits puissance, de 1 à 5
bool bit2Ventilation[3] = {};		// 3 bits ventilation de 1 à 6
bool bit2Mode[3] = {0,0,0};			// 3 bits on = 2, off = 0, auto = 4

void log(string a){
	//Dé commenter pour avoir les logs
	cout << a << endl;
}

//Fonction de passage du programme en temps réel (car la réception se joue a la micro seconde près)
void scheduler_realtime() {
	struct sched_param p;
	p.__sched_priority = sched_get_priority_max(SCHED_RR);
	if( sched_setscheduler( 0, SCHED_RR, &p ) == -1 ) {
		perror("Failed to switch to realtime scheduler.");
	}
}

//Fonction de remise du programme en temps standard
void scheduler_standard() {
	struct sched_param p;
	p.__sched_priority = 0;
	if( sched_setscheduler( 0, SCHED_OTHER, &p ) == -1 ) {
		perror("Failed to switch to normal scheduler.");
	}
}

//Calcul le nombre 2^chiffre indiqué, fonction utilisé par itob pour la conversion décimal/binaire
unsigned long power2(int power){
	unsigned long resultat=1;
	for (int i=0; i<power; i++){
		resultat*=2;
	}
	return resultat;
} 

/*
* Converti un nombre décimal en binaire.
* @param dest : tableau de destination
* @param intValue : la valeur à convertir
* @param length : le nombre de bits à générer
*/
void iToB(bool* dest, unsigned long intValue, int length){
	for (int i=0; i<length; i++){
		if ((intValue / power2(length-1-i))==1){
			intValue-=power2(length-1-i);
			dest[i]=1;
		}else{
			dest[i]=0;
		}
	}
}

/*
* Envoi d'un bit. 
* @param value : la valeur du bit à envoyer
*/
void sendBit(bool value) {
	if (value) {
		digitalWrite(txPin, HIGH);
		delayMicroseconds(dureeFront);
		digitalWrite(txPin, LOW);
		delayMicroseconds(dureeFront);  
	} else {
		digitalWrite(txPin, LOW);
		delayMicroseconds(dureeFront);
		digitalWrite(txPin, HIGH);
		delayMicroseconds(dureeFront);   
	}
}












int main (int argc, char** argv)
{
	if (setuid(0)) {
		perror("setuid");
		return 1;
	}
	
	//Si on ne trouve pas la librairie wiringPI, on arrête l'exécution
	if(wiringPiSetup() == -1) {
		log("Librairie Wiring PI introuvable, veuillez lier cette librairie...");
		return -1;
	}

	log("Démarrage du programme");

	//N° du pin d'émission (au sens WiringPi)
	txPin = atoi(argv[1]);
	
	//Configuration du pin de transmission en sortie
	pinMode(txPin, OUTPUT);
	log("Pin GPIO configuré en sortie");

	int commande = atoi(argv[2]);
	
	int puissance = atoi(argv[3]);
	
	int ventilation = atoi(argv[4]);

	iToB(bit2Mode, commande, 3);
	
	bit2EmetteurCode1 = bit2Message[0];
	bit2EmetteurCode2 = bit2Message[1];
	bit2EmetteurCode3 = bit2Message[2];
	bit2Donnee1 = bit2Message[3];
	bit2Code1 = bit2Message[4];
	bit2Donnee2 = bit2Message[5];
	bit2Code2 = bit2Message[6];
	
	
	iToB(bit2EmetteurCode1, emetteurCode1, 12);
	iToB(bit2EmetteurCode2, emetteurCode2, 12);
	iToB(bit2EmetteurCode3, emetteurCode3, 12);
	iToB(bit2Code1, code1, 12);
	iToB(bit2Code2, code2, 12);
	
	iToB(bit2Puissance, puissance, 3);
	iToB(bit2Ventilation, ventilation, 3);
	
	
	// Construction du tableau bit2Donnee1
	bit2Donnee1[0] = 1;
	bit2Donnee1[1] = bit2Ventilation[0];
	bit2Donnee1[2] = bit2Ventilation[1];
	bit2Donnee1[3] = bit2Ventilation[2];
	bit2Donnee1[4] = bit2Puissance[0];
	bit2Donnee1[5] = bit2Puissance[1];
	bit2Donnee1[6] = bit2Puissance[2];
	bit2Donnee1[7] = bit2Mode[0];
	bit2Donnee1[8] = bit2Mode[1];
	bit2Donnee1[9] = bit2Mode[2];
	int nbBitA1 = 0;
	for(int i=0; i < 10; i++){
		if(bit2Donnee1[i]) nbBitA1++;
	}
	bit2Donnee1[10] = nbBitA1%2 == 0;
	bit2Donnee1[11] = 1;
	
	// Construction du tableau bit2Donnee2
	bit2Donnee2[0] = 1;
	bit2Donnee2[1] = (bit2Ventilation[0]^bit2Ventilation[1])^bit2Puissance[2];
	bit2Donnee2[2] = !(bit2Ventilation[1]^bit2Ventilation[2]);
	bit2Donnee2[3] = !(((ventilation%2 == 0)^bit2Puissance[0])^bit2Mode[1]);
	bit2Donnee2[4] = !bit2Puissance[0];
	bit2Donnee2[5] = bit2Ventilation[0]^bit2Puissance[1];
	bit2Donnee2[6] = bit2Ventilation[1]^bit2Puissance[2];
	bit2Donnee2[7] = (ventilation%2 == 0);
	bit2Donnee2[8] = !(bit2Puissance[0]^bit2Mode[1]);
	bit2Donnee2[9] = 0;
	nbBitA1 = 0;
	for(int i=0; i < 10; i++){
		if(bit2Donnee2[i]) nbBitA1++;
	}
	bit2Donnee2[10] = nbBitA1%2 == 0;
	bit2Donnee2[11] = 1;
	
	for(int i =0; i < 7; i++){
		for(int j=0; j<12; j++){
		cout << bit2Message[i][j];
		}
		cout << endl;
	}
	
	
	//On passe en temps réel
	scheduler_realtime();
	
	//Envoi de la trame 5 fois de suite
	for(int i=0; i<nbEnvois; i++){
		digitalWrite(txPin, LOW);
		for(int j =0; j < 7; j++){
			digitalWrite(txPin, HIGH);
			delayMicroseconds(dureeInterDonnees);
			for(int k=0; k<12; k++){
				sendBit(bit2Message[j][k]);
			}
		}
		digitalWrite(txPin, LOW);
		delayMicroseconds(dureeInterMessage);
	}
	
	
	//On revient en mode normal
	scheduler_standard();
	
	log("fin du programme");
}

