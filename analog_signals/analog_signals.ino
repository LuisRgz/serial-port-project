#include <Servo.h>
// Configurar entradas
const int analogPins[] = {A0, A1, A2, A3, A4};

const int ledButtonJ = 3;
const int ledButtonON = 4;
const int ledButtonOFF = 5;

//Configurar salidas
const int ledPIN = 9;

// Constantes de funcinalidad
const int analogSize = sizeof(analogPins)/sizeof(analogPins[0]);
const char action1 = 'A';
const char action2 = 'B';
const char action3 = 'C';
const char ledOn = 'T';
const char ledOff = 'O';
const char start = 'L';
const char end = 'M';

// variables de lectura de datos
int values[analogSize];
int buttonONState = 0;
int buttonOFFState = 0;
int buttonJState = 0;

// variable de control de datos
bool sendData = false;

void setup() {
  // Inicialización de comunicación Serial
  Serial.begin(9600);
  // Se inicializan los pines de lectura/escritura
  pinMode(ledPIN , OUTPUT);
  pinMode(ledButtonON , INPUT);
  pinMode(ledButtonOFF , INPUT);
  pinMode(ledButtonJ, INPUT_PULLUP);
}
 
void loop() {
  // Leer valores analógicos
  for (byte i = 0; i < analogSize; i++) {
      values[i] = analogRead(analogPins[i]);
    }


  // Leer valores digitales
  buttonONState = digitalRead(ledButtonON);
  buttonOFFState = digitalRead(ledButtonOFF);
  buttonJState = digitalRead(ledButtonJ);

  // Define si alguna acción fue activada
  char action='.';
  if (buttonONState == HIGH) {
    action = action1;
  }
  if (buttonOFFState == HIGH) {
    action = action2;
  }
  if (buttonJState == LOW) {
    action = action3;
  }

  // Validar si se envía información
  if (sendData)
  {
    //Envía la información separada por " " (espacio en blanco)
    Serial.print(action);
    for (byte i = 0; i < analogSize; i++) {
      Serial.print(" ");
      Serial.print(values[i]);
    }
    Serial.print("\n");
  }

  //Leer opciones
  char option = Serial.read();

  // Control de led
  if (option == ledOn)
  {
    digitalWrite(ledPIN , HIGH);
  }
  if (option == ledOff)
  {
    digitalWrite(ledPIN , LOW);
  }

  // Control de envío datos
  if (option == end)
  {
    sendData=false;
  } 
  if (option == start)
  {
    sendData=true;
  } 

  // Tiempo de espera
  delay(50);
}