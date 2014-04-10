/*
 * Code pour construction d'un recepteur "maison"
 * Fréquence : 433.92 mhz
 * Protocole : perso (basé sur home easy) 
 * Licence : CC -by -sa
 * Matériel associé : Atmega 328 (+résonateur associé) + récepteur RF AM 433.92 mhz + relais + led d'etat
 * Auteur : Christophe SAILLY
 * 
 * Basé sur le travail de :
 * Valentin CARRUESCO  aka idleman (idleman@idleman.fr - http://blog.idleman.fr)
 * Barnaby Gray 12/2008
 * Peter Mead   09/2009
 */

#include <EEPROM.h>

int rxPin = 9;						// N° du pin utilisé pour la reception des données
int relayPin = 10;
int ledPin = 11;
unsigned int receptorId = 2731;		// Identifiant du récepteur
unsigned int senderId	= 3259;		// Identifiant de l'émetteur autorisé

//Durées des vérrous en microsecondes
int dureeVerrou1 = 9900; //9900
int dureeVerrou2 = 2675;
int dureeVerrou3 = 2675;
//Durées des fronts bas en microsecondes
int dureeFrontBasZero = 310; //275 orinally, but tweaked.
int dureeFrontBasUn = 1340; //1225 orinally, but tweaked.
//Durée des fronts haut en microsecondes
int dureeFrontHaut = 310; //275 orinally, but tweaked.
//Marge d'erreur sur la durée des frontsBas en microsecondes
int margeErreur = 100;

struct config_t
{
  long sender;
  int receptor;
} 
signal;

struct signal_t
{
  long sender;
  int receptor;
  boolean isSignal;
  boolean state;
} 
receivedSignal;


void setup()
{
  pinMode(rxPin, INPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("start");
  digitalWrite(ledPin,HIGH);
}


void loop()
{
  //Ecoute des signaux
  listenSignal();

}


bool isVerrou(int t, int verrou){
	return (t > verrou-100 && t < verrou+100);
}


void listenSignal(){
  receivedSignal.sender = 0;
  receivedSignal.receptor = 0;

  int i = 0;
  unsigned long t = 0;

  byte prevBit = 0;
  byte bit = 0;

  unsigned int sender = 0;
  unsigned int receptor = 0;
  unsigned int sendorType = 0;
  unsigned int sendType = 0;
  unsigned int datasLength = 0;
  unsigned int datas = 0;
  unsigned int crc16 = 0;
  int *tableau = NULL;
  
  unsigned long t_latch1 = 0;
  unsigned long t_latch2 = 0;
  unsigned long t_latch3 = 0;

  // verrou 1
  while(!isVerrou(t,dureeVerrou1)){
    t = pulseIn(rxPin, LOW, 1000000); 
  }
  t_latch1 = t;

  // verrou 2    
  t = pulseIn(rxPin, LOW, 1000000);
  if(!isVerrou(t,dureeVerrou2)){
    Serial.print("Verrou1 : ");
    Serial.println(t_latch1);
    Serial.print("Verrou2 erroné : ");
    Serial.println(t);
    return;
  }
  t_latch2 = t;

  // datas
  t = pulseIn(rxPin, LOW, 1000000);
  
 do{
    if(t > dureeFrontBasZero-margeErreur && t < dureeFrontBasZero+margeErreur) {
      bit = 0;                    
    } 
    else if(t > dureeFrontBasUn-margeErreur && t < dureeFrontBasUn+margeErreur) {
      bit = 1;                      
    } 
    else {
      Serial.print("bit ");
      Serial.print(i);
      Serial.print(" mort : ");
      Serial.println(t);
      return;  
    }

    if(i % 2 == 1) {
      if((prevBit ^ bit) == 0) {	// must be either 01 or 10, cannot be 00 or 11
        return;
      }
      if(i <= 24) {	// 12 bits sender
        sender <<= 1;
        sender |= prevBit;
      } else if ( i > 24 && i <= 48 ) {	// 12 bits receptor
        receptor <<= 1;
        receptor |= prevBit;
      } else if ( i > 48 && i <= 60 ) {	// 6 bits sendor type
        sendorType <<= 1;
	sendorType |= prevBit;
      } else if ( i > 60 && i <= 64 ) {	// 2 bits send type
        sendType <<= 1;
	sendType |= prevBit;
      } else if ( i > 64 && i <= 80 ) {	// 8 bits datas length
        datasLength <<= 1;
	datasLength |= prevBit;
      } else if ( i > 80 && i <= (80 + 2 * datasLength * 8 ) ) {	// n * 8 bits of datas and 16 bits of crc16 control
        if (tableau == NULL){
          tableau = (int*)realloc ( tableau , datasLength * sizeof(int) );
        }
        
        datas <<= 1;
	datas |= prevBit;
      } else if (i > (80 + 2 * datasLength * 8 ) && i <= (80 + 2 * datasLength * 8 + 32)) { //32 bits of crc16 control
	crc16 <<= 1;
	crc16 |= prevBit;	
      } else {
        
      }
    }

    prevBit = bit;
    ++i;
	 t = pulseIn(rxPin, LOW, 1000000);
  }while(!isVerrou(t,dureeVerrou3));
  

  t_latch3 = t;

Serial.println("++++++++++++++++");
Serial.print("Verrou1 : ");
Serial.println(t_latch1);
Serial.print("Verrou2 : ");
Serial.println(t_latch2);
Serial.print("Verrou3 : ");
Serial.println(t_latch3);
Serial.print("sender :");
Serial.println(sender);
Serial.print("receptor :");
Serial.println(receptor);
Serial.print("sendorType :");
Serial.println(sendorType);
Serial.print("sendType :");
Serial.println(sendType);
Serial.print("datasLength :");
Serial.println(datasLength);
Serial.print("datas :");
Serial.println(datas);
Serial.print("crc16 :");
Serial.println(crc16);
Serial.println("+++++++++++++++++");
free(tableau);
}





