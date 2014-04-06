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

sudo ./emetteur <txPin> <puissance> <ventilation>

<puissance> -> puissance de chauffe de 1 à 5
<ventilation> -> ventilation de 1 à 6. 6 = auto.

sudo ./emetteur 0 2 6  

*/

using namespace std;

//Durée start
int dureeStart = 1250;
//Durée fronts
int dureeFront = 390;
//Durée entre 2 données
int dureeInterDonnees = 1250;
//Durée entre 2 messages
int dureeInterMessage = 5080;
//Nombre d'envois du message
int nbEnvois = 5;



bool bit2EmetteurCode1[12]={};		// 12 bits Identifiant partie 1 émetteur
bool bit2EmetteurCode2[12]={};		// 12 bits Identifiant partie 2 émetteur
bool bit2EmetteurCode3[12]={};		// 12 bits Identifiant partie 3 émetteur
bool bit2Donnee1[12]={};			// 12 bits Donnée 1
bool bit2Code1[12]={};				// 12 bits Code 1
bool bit2Donnee2[12]={};			// 12 bits Donnée 2
bool bit2Code2[12]={};				// 12 bits Code 2

int txPin;						// N° du pin utilisé pour l'envoi des données


bool bit2Message[7][12]={bit2EmetteurCode1,bit2EmetteurCode2,bit2EmetteurCode3,bit2Donnee1,bit2Code1,bit2Donnee2,bit2Code2};

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

	int puissance = atoi(argv[2]);
	
	int ventilation = atoi(argv[3]);
	
	//On passe en temps réel
	scheduler_realtime();
	
	//Envoi de la trame 5 fois de suite
	for(int i=0; i<nbEnvois; i++){

	}
	
	
	//On revient en mode normal
	scheduler_standard();
	
	log("fin du programme");
}

