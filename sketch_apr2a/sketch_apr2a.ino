#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

const int LDR_PIN = 34;  // GPIO Pin 34
const char* ssid = "ssid"; 
const char* password = "password"; 
const char* mqtt_server = "ip-address";

#define SS_PIN 5  // SDA Pin
#define RST_PIN 4 // RST Pin
#define LDR_PIN 34  // SDA Pin

MFRC522 rfid(SS_PIN, RST_PIN); // MFRC522 instance


WiFiClient espClient;
PubSubClient client(espClient);


void setup() {
  Serial.begin(115200);
  //WI-FI
  setup_wifi(); 
  client.setServer(mqtt_server, 1883);  
  client.setCallback(callback);

  // Light
  analogReadResolution(12);  // ADC Voltage

  // RFID
  SPI.begin();  
  rfid.PCD_Init();  
  Serial.println("Place your RFID card near the reader...");
}


void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);


  WiFi.begin(ssid, password);


  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void callback(String topic, byte* message, unsigned int length) {
  String messagein = "";
  for (int i = 0; i < length; i++) {
    messagein += (char)message[i];
  }
  Serial.print("Message on topic: ");
  Serial.println(messagein);

  if (topic == "light/led") {
    if (messagein == "ON") {
      Serial.println("Light is ON"); // Publish ON
    } else if (messagein == "OFF") {
      Serial.println("Light is OFF"); // Publish OFF
    }
  }
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
      client.subscribe("light/led"); // For Light 
      client.subscribe("user/rfid"); // For RFID

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);  
    }
  }
}


void loop() {
  if (!client.connected()) {
    reconnect();  
  }
  client.loop();  

  int ldrValue = analogRead(LDR_PIN);
  char lightValues[10];
  dtostrf(ldrValue, 4, 2, lightValues);  
  client.publish("IoTlab/ESP32", lightValues);
  delay(1000);

  if (!rfid.PICC_IsNewCardPresent()) {
    return;  // If no card is detected
  }


  if (!rfid.PICC_ReadCardSerial()) {
    return;  // If RFID reader is unable to read card serial number
  }


  // RFID number
  String tag = "";
  Serial.println("Card detected!");
  for (byte i = 0; i < rfid.uid.size; i++) {
    tag += String(rfid.uid.uidByte[i], HEX);  // Convert to hex value
    if (i < rfid.uid.size - 1) {
      tag += "";  
    }
  }
  Serial.print("Card UID: ");
  Serial.println(tag);

  client.publish("user/rfid", tag.c_str());
  delay(1000);

  rfid.PICC_HaltA();
}