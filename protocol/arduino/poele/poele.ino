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
#include <avr/pgmspace.h>

static PROGMEM prog_uint32_t crc_table[16] = {
	0x00000000, 0x1db71064, 0x3b6e20c8, 0x26d930ac,
	0x76dc4190, 0x6b6b51f4, 0x4db26158, 0x5005713c,
	0xedb88320, 0xf00f9344, 0xd6d6a3e8, 0xcb61b38c,
	0x9b64c2b0, 0x86d3d2d4, 0xa00ae278, 0xbdbdf21c
};


// N° du pin utilisé pour la réception des données
int rxPin = 9;
//N° des pin des relais
int pinOn = 1;
int pinRemote = 2;
int pinOff = 3;
int pinLow = 4;
int pinMedium = 5;
int pinHigh = 6;

int relayPin = 10;

// Identifiant du récepteur
unsigned int receptorId = 2731;
// Identifiant de l'émetteur associé
unsigned int senderId	= 3259;		

//Durées des vérrous en microsecondes
int dureeVerrou1 = 9900;
int dureeVerrou2 = 2675;
int dureeVerrou3 = 2675;
//Durées des fronts bas en microsecondes
int dureeFrontBasZero = 310;
int dureeFrontBasUn = 1340;
//Durée des fronts haut en microsecondes
int dureeFrontHaut = 310;
//Marge d'erreur sur la durée des frontsBas en microsecondes
int margeErreur = 100;

//Dernier crc reçu.
unsigned long dernierCrc = 0;

//Masque utilisé pour récupérer la valeur des 3bits représentant le switch de mode (on-remote-off)
int mask1 = 199;//11000111
//Masque utilisé pour récupérer la valeur des 3bits représentant le switch de puissance (low-medium-high)
int mask2 = 248;//111110001

int on = 1;//00000001
int remote = 2;//00000010
int off = 4;//00000100

int low = 8;//00001000
int medium = 16;//00010000
int high = 32;//00100000

void setup()
{
	pinMode(rxPin, INPUT);
	
	pinMode(pinOn, OUTPUT);
	pinMode(pinRemote, OUTPUT);
	pinMode(pinOff, OUTPUT);
	pinMode(pinLow, OUTPUT);
	pinMode(pinMedium, OUTPUT);
	pinMode(pinHigh, OUTPUT);
	
	pinMode(relayPin, OUTPUT);
	Serial.begin(9600);
	Serial.println("start");
}


void loop()
{
	//Ecoute des signaux
	listenSignal();
}

unsigned long crc_update(unsigned long crc, byte data)
{
	byte tbl_idx;
	tbl_idx = crc ^ (data >> (0 * 4));
	crc = pgm_read_dword_near(crc_table + (tbl_idx & 0x0f)) ^ (crc >> 4);
	tbl_idx = crc ^ (data >> (1 * 4));
	crc = pgm_read_dword_near(crc_table + (tbl_idx & 0x0f)) ^ (crc >> 4);
	return crc;
}

unsigned long crc_string(char *s, int nbByte)
{
	unsigned long crc = ~0L;
	for(int i=0; i < nbByte; i++){
		crc = crc_update(crc, *s++);
	}
	crc = ~crc;
	return crc;
}

//Détermine si un temps t correspond au temps du verrou, + ou - 100
bool isVerrou(int t, int verrou){
	return (t >= verrou-100 && t <= verrou+100);
}

//Convertit 8 bits d'un tableau de bit en char, à partir de la position start 
unsigned char bitsToChar(bool* src, int start){
	unsigned char result = 0;
	for (int i = 0; i < 8; ++i ){
		result |= (src[start+i]) << (7 - i);
	}
	return result;
}

void listenSignal(){
	int bitIdx = 0;
	unsigned long t = 0;

	byte prevBit = 0;
	byte currBit = 0;

	unsigned int sender = 0;
	unsigned int receptor = 0;
	unsigned int sendorType = 0;
	unsigned int sendType = 0;
	unsigned int nbByteOfData = 0;
	unsigned int datas = 0;
	unsigned long crc32 = 0;
	int *datasTab = NULL;
	int byteDataBitIdx = 0; //Permet de compter le nombre de bit de données reçus
	int byteDataIdx = 0;     //Permet de compter le nombre de bytes de données reçus

	bool* bitMessage=(bool*)malloc(48 * sizeof(bool));//Permet de stocker la trame reçue sous forme de bit.
	int msgIdx = 0;//Index du bit du message courant

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
		//Serial.print("Verrou1 : ");
		//Serial.println(t_latch1);
		//Serial.print("Verrou2 erroné : ");
		//Serial.println(t);
		free(bitMessage);
		return;
	}
	t_latch2 = t;

	// datas
	t = pulseIn(rxPin, LOW, 1000000);

	do{
		if(t > dureeFrontBasZero-margeErreur && t < dureeFrontBasZero+margeErreur) {
			currBit = 0;                    
		} 
		else if(t > dureeFrontBasUn-margeErreur && t < dureeFrontBasUn+margeErreur) {
			currBit = 1;                      
		} 
		else {
			//Serial.print("currBit ");
			//Serial.print(i);
			//Serial.print(" mort : ");
			//Serial.println(t);
			free(bitMessage);
			return;  
		}

		if(bitIdx % 2 == 1) {
			if((prevBit ^ currBit) == 0) {	// must be either 01 or 10, cannot be 00 or 11
				free(bitMessage);
				return;
			}
			
			if(bitIdx <= 24) {	// 12 bits sender
				sender <<= 1;
				sender |= prevBit;
				bitMessage[msgIdx++] = (prevBit == 1);
				if (bitIdx == 23 && sender != senderId){
					free(bitMessage);
					return;
				}
			} else if ( bitIdx > 24 && bitIdx <= 48 ) {	// 12 bits receptor
				receptor <<= 1;
				receptor |= prevBit;
				bitMessage[msgIdx++] = (prevBit == 1);
				if (bitIdx == 47 && (receptorId != receptor)){
					free(bitMessage);
					return;
				}
			} else if ( bitIdx > 48 && bitIdx <= 60 ) {	// 6 bits sendor type
				sendorType <<= 1;
				sendorType |= prevBit;
				bitMessage[msgIdx++] = (prevBit == 1);
			} else if ( bitIdx > 60 && bitIdx <= 64 ) {	// 2 bits send type
				sendType <<= 1;
				sendType |= prevBit;
				bitMessage[msgIdx++] = (prevBit == 1);
			} else if ( bitIdx > 64 && bitIdx <= 80 ) {	// 8 bits datas length
				nbByteOfData <<= 1;
				nbByteOfData |= prevBit;
				bitMessage[msgIdx++] = (prevBit == 1);
				if (bitIdx == 80){
					bitMessage=(bool*)realloc(bitMessage,(40 +  nbByteOfData * 8 )* sizeof(bool));
				}
			} else if ( bitIdx > 80 && bitIdx <= (80 + 2 * nbByteOfData * 8 ) ) {	// n * 8 bits of datas and 16 bits of crc32 control
				if (datasTab == NULL){
					datasTab = (int*)realloc ( datasTab , nbByteOfData * sizeof(int) );
				}        
				datas <<= 1;
				datas |= prevBit;
				if (++byteDataBitIdx == 8){
					datasTab[byteDataIdx] = datas;
					datas = 0;
					++byteDataIdx;
					byteDataBitIdx = 0;
				}
				bitMessage[msgIdx++] = (prevBit == 1);
			} else if (bitIdx > (80 + 2 * nbByteOfData * 8 ) && bitIdx <= (80 + 2 * nbByteOfData * 8 + 64)) { //64 bits of crc32 control
				crc32 <<= 1;
				crc32 |= prevBit;	
			}
		}
		prevBit = currBit;
		++bitIdx;
		t = pulseIn(rxPin, LOW, 1000000);
	}while(!isVerrou(t,dureeVerrou3));

	t_latch3 = t;

	//Calcul du crc32
	int nbByte = msgIdx/8;
	//Serial.println(nbByte);
	//Serial.print("Message : ");
	char *charMessage = (char*)malloc(nbByte * sizeof(char));		
	for(int i=0; i < nbByte; i++){
		unsigned char res = bitsToChar(bitMessage, i*8);
		charMessage[i] = res;
		//Serial.print(res, HEX);
	}
	//Serial.println("");
	unsigned long  crc32_calc = crc_string(charMessage,nbByte);




	//Si le crc est ok et que le message est différent du dernier message reçu
	if (crc32_calc == crc32 && dernierCrc != crc32){
		dernierCrc = crc32;      
		digitalWrite(relayPin,HIGH); // met la broche au niveau haut (5V) – allume la LED
		delay(1000); // pause de 500 millisecondes (ms)
		digitalWrite(relayPin,LOW); // met la broche au niveau bas (0V) – éteint la LED
	}
	
	Serial.println("++++++++++++++++");
	//Serial.print("Verrou1 : ");
	//Serial.println(t_latch1);
	//Serial.print("Verrou2 : ");
	//Serial.println(t_latch2);
	//Serial.print("Verrou3 : ");
	//Serial.println(t_latch3);
	Serial.print("sender :");
	Serial.println(sender);
	Serial.print("receptor :");
	Serial.println(receptor);
	Serial.print("sendorType :");
	Serial.println(sendorType);
	Serial.print("sendType :");
	Serial.println(sendType);
	Serial.print("nbByteOfData :");
	Serial.println(nbByteOfData);
	for(int i=0; i<nbByteOfData; i++){
		Serial.print("datas (");
		Serial.print(i);
		Serial.print(") :");
		Serial.println(datasTab[i]);
	}
	Serial.print("crc32     :");
	Serial.println(crc32, HEX);
	Serial.print("crc32 calc:");
	Serial.println(crc32_calc, HEX);
	Serial.println("+++++++++++++++++");

	if ((datasTab[0] & mask1) == on){
		if ((datasTab[0] & mask2) == low){
			Serial.println("Low");
			digitalWrite(pinMedium,LOW);
			digitalWrite(pinHigh,LOW);
			digitalWrite(pinLow,HIGH);
			
			digitalWrite(pinOff,LOW);
			digitalWrite(pinRemote,LOW);
			digitalWrite(pinOn,HIGH);
		}else if ((datasTab[0] & mask2) == medium){
			Serial.println("Medium");
			digitalWrite(pinLow,LOW);
			digitalWrite(pinHigh,LOW);
			digitalWrite(pinMedium,HIGH);
			
			digitalWrite(pinOff,LOW);
			digitalWrite(pinRemote,LOW);
			digitalWrite(pinOn,HIGH);
		}else if((datasTab[0] & mask2) == high){
			Serial.println("High");
			digitalWrite(pinLow,LOW);
			digitalWrite(pinMedium,LOW);
			digitalWrite(pinHigh,HIGH);
			
			digitalWrite(pinOff,LOW);
			digitalWrite(pinRemote,LOW);
			digitalWrite(pinOn,HIGH);
		}else{
			Serial.println("Defaut1 => Off");
			digitalWrite(pinOn,LOW);
			digitalWrite(pinRemote,LOW);
			digitalWrite(pinOff,HIGH);
		}
	}else if ((datasTab[0] & mask1) == remote){
		Serial.println("Remote");
		digitalWrite(pinOn,LOW);
		digitalWrite(pinOff,LOW);
		digitalWrite(pinRemote,HIGH);					
	}else if ((datasTab[0] & mask1) == off){
		Serial.println("Off");
		digitalWrite(pinOn,LOW);
		digitalWrite(pinRemote,LOW);
		digitalWrite(pinOff,HIGH);
	}else{
		Serial.println("Defaut2 => Off");
		digitalWrite(pinOn,LOW);
		digitalWrite(pinRemote,LOW);
		digitalWrite(pinOff,HIGH);
	}
	
	free(charMessage);
	free(bitMessage);
	free(datasTab);
}
