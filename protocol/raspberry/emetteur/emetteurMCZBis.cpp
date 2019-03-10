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

sudo ./emetteur <txPin> <trame>

sudo ./emetteur 0 1001101001....01100101

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

int txPin;							// N° du pin utilisé pour l'envoi des données

bool bit2Message[7][12]={};

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

	
	if (strlen(argv[2]) != 12*7){
		log("Longueur message invalide");
		exit(0);
	}
	
	for(int i =0; i < 7; i++){
		for(int j=0; j<12; j++){
			if (argv[2][12*i+j]  == '0'){
				bit2Message[i][j] = 0;
			}else if (argv[2][12*i+j] == '1'){
				bit2Message[i][j] = 1;
			}
		}
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

