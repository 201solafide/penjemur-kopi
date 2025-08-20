#include <DHT.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>

// Definisi pin untuk sensor DHT
#define DHTPIN 2
#define DHTTYPE DHT11


// Definisi pin untuk sensor BMP280
#define BMP_SCK  (13)
#define BMP_MISO (12)
#define BMP_MOSI (11)
#define BMP_CS   (10)


// Definisi pin untuk sensor hujan
#define RAINPIN A2


// Inisialisasi objek sensor DHT dan BMP280
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP280 bmp(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);


void setup() {
    // Memulai sensor DHT
    dht.begin();


    // Memulai sensor BMP280
    bmp.begin();


    // Mengatur pin untuk sensor hujan sebagai input
    pinMode(RAINPIN, INPUT);


    // Mengatur parameter sampling dan standby untuk sensor BMP280
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2, Adafruit_BMP280::SAMPLING_X16, Adafruit_BMP280::FILTER_X16, Adafruit_BMP280::STANDBY_MS_500);


    // Memulai komunikasi serial dengan baud rate 9600
    Serial.begin(9600);
}


void loop() {
    // Mengecek apakah ada data yang tersedia di Serial
    if (Serial.available() > 0) {
        // Membaca satu baris data dari Serial
        String line = Serial.readStringUntil('\n');


        // Memeriksa apakah baris data adalah "OK"
        if (line == "OK") {
            // Membaca kelembaban dan suhu dari sensor DHT
            float h = dht.readHumidity();
            float t = bmp.readTemperature();
            float T = dht.readTemperature();


            // Membaca tekanan atmosfer dari sensor BMP280
            float p = bmp.readPressure();


            // Membaca nilai basah (wet) dari sensor hujan
            float w = 1023 - analogRead(RAINPIN);


            // Menampilkan data kelembaban, suhu, tekanan, dan nilai basah melalui Serial
            Serial.print("hum:");
            Serial.print(h);
            Serial.print(",tmpBMP:");
            Serial.print(t);
            Serial.print(",tmpDHT:");
            Serial.print(T);
            Serial.print(",pre:");
            Serial.print(p);
            Serial.print(",wet:");
            Serial.print(w);
            Serial.print("\n");


            // Memberi jeda 500 milidetik
            delay(500);
        }
    }
}
