#include <wiringPi.h>
#include <iostream>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <stdlib.h>
#include <sched.h>
#include <sstream>
#include <string.h>
#include "lib_crc.h"

/*
Basé sur le travail de Idleman (idleman@idleman.fr - http://blog.idleman.fr)
Licence : CC by sa


g++ emetteur.cpp lib_crc.c -o emetteur -lwiringPi

sudo ./emetteur <txPin> <emetteur> <recepteur> <typeEmetteur> <typeEmission> [<octetDonnee>,...]

sudo ./emetteur 0 1234 2345 33 2 128  

*/

using namespace std;

//Durées des verrous en microsecondes
int dureeVerrou1 = 9900;
int dureeVerrou2 = 2675;
int dureeVerrou3 = 2675;
//Durées des fronts bas en microsecondes
int dureeFrontBasZero = 310;
int dureeFrontBasUn = 1340;
//Durée des fronts haut en microsecondes
int dureeFrontHaut = 310;
//Nombre d'envois du message
int nbEnvois = 5;
//Durée entre 2 envois en millisecondes
int delaiEnvois = 20;

int txPin;						// N° du pin utilisé pour l'envoi des données
bool bit2Emetteur[12]={};       // 12 bit Identifiant émetteur
bool bit2Recepteur[12]={};    	// 12 bit Identifiant récepteur
bool bit2TypeEmetteur[6]={};	// 6 bit Type d'émetteur
bool bit2TypeEmission[2]={};	// 2 bit Type d'émission
bool bit2LongueurDonnees[8]={};	// 8 bit Longueur des données
bool bit2Donnees[8]={};			// 8 bit de données
bool bit2Crc32[32]={};			// 32 bit de contrôle

bool* message=NULL;			//Message complet sans crc32. 48 bits minimum

int msgIdx = 0;

int recepteur;               	// Identifiant récepteur
int emetteur;					// Identifiant émetteur
int typeEmetteur;				// Type émetteur
int typeEmission;				// Type récepteur
int longueurDonnees;			// Longueur données
int donnees;					// Données



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
			message[msgIdx++] = 1;
		}else{
			dest[i]=0;
			message[msgIdx++] = 0;
		}
	}
}

/*
* Envoi d'un bit. Un front haut fixe et un front bas fonction du bit à envoyer
* 1 = 310µs haut puis 1340µs bas
* 0 = 310µs haut puis 310µs bas
* @param value : la valeur du bit à envoyer
*/
void sendBit(bool value) {
	if (value) {
		digitalWrite(txPin, HIGH);
		delayMicroseconds(dureeFrontHaut);
		digitalWrite(txPin, LOW);
		delayMicroseconds(dureeFrontBasUn);  
	} else {
		digitalWrite(txPin, HIGH);
		delayMicroseconds(dureeFrontHaut);
		digitalWrite(txPin, LOW);
		delayMicroseconds(dureeFrontBasZero);   
	}
}

/*
* Envoi d'un bit en codage Manchester.
* 0 = 01
* 1 = 10
* @param value : la valeur du bit à envoyer
*/
void sendPair(bool value) {
	if(value){
		sendBit(true);
		sendBit(false);
	}else{
		sendBit(false);
		sendBit(true);
	}
}

/*
* Envoi un tableau de booléens 
* @param src : pointeur sur le tableau à envoyer
* @param size : taille du tableau
*/
void envoyerMessage(bool *src, int size){
	for(int i = 0; i < size; i++){
		sendPair(src[i]);
	}
}

/*
* Envoi un verrou
* @param durée : durée du verrou en micro secondes
*/
void envoyerVerrou(int duree){
	//On passe à l'état haut
	digitalWrite(txPin, HIGH);
	delayMicroseconds(dureeFrontHaut);   
	//On passe à l'état bas le temps du verrou	
	digitalWrite(txPin, LOW);
	delayMicroseconds(duree);
	//on revient à l'état Haut
	digitalWrite(txPin, HIGH); 
}

/*
* Envoi la trame complète.
*/
void envoyerTrame(bool *src, int size){
	// Séquence de verrous annonçant le départ du signal au récepteur
	envoyerVerrou(dureeVerrou1);     
	envoyerVerrou(dureeVerrou2);
	// Le message
	envoyerMessage(src,size);
	// Verrou pour signaler la fermeture du signal
	envoyerVerrou(dureeVerrou3);
}

/*
* Converti 8 bits d'un tableau de bits en 1 char, à partir de la position start
* @param src : le tableau de bits
* @param start : index de début
*/
unsigned char bToChar(bool* src, int start){
	unsigned char result = 0;
	for (int i = 0; i < 8; ++i ){
		result |= (src[start+i]) << (7 - i);
	}
	return result;
}

/*
* Calcul du crc32 d'un tableau de bit
* @param src : le tableau de bits
* @param nbByte : nombre d'octets du tableau
*/
int calculCrc32(bool* src, int nbByte){
	unsigned long crc_32 = 0xffffffffL;
	
	for(int i=0; i < nbByte; i++){
		unsigned char res = bToChar(src, i*8);
		crc_32 = update_crc_32(crc_32,res);
	}
	
	crc_32    ^= 0xffffffffL;
	
	//printf("\nCRC32 : 0x%08lX \n",crc_32);
	
	return crc_32;
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

	//Identifiant émetteur
	emetteur = atoi(argv[2]);

	//Identifiant récepteur
	recepteur = atoi(argv[3]);

	//Type émetteur
	typeEmetteur = atoi(argv[4]);

	//Type émission
	typeEmission = atoi(argv[5]);

	//Longueur données
	longueurDonnees = argc - 6;
	
	//Configuration du pin de transmission en sortie
	pinMode(txPin, OUTPUT);
	log("Pin GPIO configuré en sortie");

	//Allocation du message
	int tailleMessage = (40 + longueurDonnees * 8);
	message = (bool*) malloc(tailleMessage * sizeof(bool));
	
	//Conversion du code de l'émetteur en code binaire
	iToB(bit2Emetteur,emetteur,(int)sizeof bit2Emetteur);
	
	//Conversion du code du récepteur en code binaire
	iToB(bit2Recepteur,recepteur,(int)sizeof bit2Recepteur);
	
	//Conversion du type de l'émetteur en code binaire
	iToB(bit2TypeEmetteur,typeEmetteur,(int)sizeof bit2TypeEmetteur);

	//Conversion du type de l'émission en code binaire
	iToB(bit2TypeEmission,typeEmission,(int)sizeof bit2TypeEmission);

	//Conversion de la longueur des données en code binaire
	iToB(bit2LongueurDonnees,longueurDonnees,(int)sizeof bit2LongueurDonnees);
	
	//Conversion des données en code binaire
	for(int i=0; i < longueurDonnees; i++){
		donnees = atoi(argv[6+i]);
		iToB(bit2Donnees,donnees,(int)sizeof bit2Donnees);
	}
	
	//Calcul du crc32
	int crc32 = calculCrc32(message,tailleMessage/8);

	printf("\ncrc : %X\n", crc32);

	//Conversion du crc32 en code binaire
	iToB(bit2Crc32,crc32,(int)sizeof bit2Crc32);
	
	//On passe en temps réel
	scheduler_realtime();
	
	//Envoi de la trame 5 fois de suite
	for(int i=0; i<nbEnvois; i++){
		//log("Envoi des données");
		envoyerTrame(message,tailleMessage+32);//Taille du message + 32 bits de crc
		delay(delaiEnvois);// attendre 20 ms (sinon le socket nous ignore)
	}
	
	
	//On revient en mode normal
	scheduler_standard();
	
	log("fin du programme");
}

