#include <DHT.h>
 
// Definimos el pin digital donde se conecta el sensor
#define DHTPIN 3
// Dependiendo del tipo de sensor
#define DHTTYPE DHT11
 
// Inicializamos el sensor DHT11
DHT dht(DHTPIN, DHTTYPE);
const int ledPIN = 9;
const int buttonPIN = 4;

int buttonState = 0;
bool sendData = false;

void setup() {
  // Inicializamos comunicación serie
  Serial.begin(9600);
  // Se inicializan los pines de lectura/escritura
  pinMode(ledPIN , OUTPUT);
  pinMode(buttonPIN , INPUT);
  // Comenzamos el sensor DHT
  dht.begin();
 
}
 
void loop() {
  // Leemos la humedad relativa
  float h = dht.readHumidity();

  // Leemos la temperatura en grados centígrados (por defecto)
  float t = dht.readTemperature();

  // Leer botón
  char action;
  buttonState = digitalRead(buttonPIN);
  if (buttonState == HIGH) {
    action = 'A';
  } else {
    action = 'B';
  }

  // Comprobamos si ha habido algún error en la lectura
  if (isnan(h) || isnan(t)) {
    Serial.println("Error obteniendo los datos del sensor DHT11");
    return;
  }

  // Validar si se envía información
  if (sendData)
  {
    Serial.print(h);
    Serial.print(" ");
    Serial.print(t);
    Serial.print(" ");
    Serial.print(action);
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