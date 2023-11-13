#include <Servo.h>

int pinA0 = A0;
int pinA1 = A1;
int pinA2 = A2;
int pinA3 = A3;

const int buttonJ = 3;
const int buttonON = 4;
const int buttonOFF = 5;

int valorA0 = 0;
int valorA1 = 0;
int valorA2 = 0;
int valorA3 = 0;
int buttonONState = 0;
int buttonOFFState = 0;
int buttonJState = 0;

const int ledPIN = 9;

bool sendData = false;

void setup() {
  // Inicializamos comunicación serie
  Serial.begin(9600);
  // Se inicializan los pines de lectura/escritura
  pinMode(ledPIN , OUTPUT);
  pinMode(buttonON , INPUT);
  pinMode(buttonOFF , INPUT);
  pinMode(buttonJ, INPUT_PULLUP);
}
 
void loop() {
  // Leer valores analógicos
  valorA0 = analogRead ( pinA0);
  valorA1 = analogRead ( pinA1);
  valorA2 = analogRead ( pinA2);
  valorA3 = analogRead ( pinA3);

  // Leer valores digitales
  buttonONState = digitalRead(buttonON);
  buttonOFFState = digitalRead(buttonOFF);
  buttonJState = digitalRead(buttonJ);

  char action='.';
  if (buttonONState == HIGH) {
    action = 'A';
  }
  if (buttonOFFState == HIGH) {
    action = 'B';
  }
  if (buttonJState == LOW) {
    action = 'C';
  }

  // Validar si se envía información
  if (sendData)
  {
    Serial.print(action);
    Serial.print(" ");
    Serial.print(valorA0);
    Serial.print(" ");
    Serial.print(valorA1);
    Serial.print(" ");
    Serial.print(valorA2);
    Serial.print(" ");
    Serial.print(valorA3);
    Serial.print("\n");
  }

  //Leer opciones
  char option = Serial.read();

  // Control de led
  if (option == 'A')
  {
    digitalWrite(ledPIN , HIGH);
  }
  if (option == 'B')
  {
    digitalWrite(ledPIN , LOW);
  }

  // Control de envío datos
  if (option == 'M')
  {
    sendData=false;
  } 
  if (option == 'L')
  {
    sendData=true;
  } 

  // Tiempo de espera
  delay(50);
}