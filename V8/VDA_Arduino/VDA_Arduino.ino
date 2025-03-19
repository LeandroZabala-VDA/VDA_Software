// Explicacion del codigo: https://www.youtube.com/watch?v=Whmb9zAmpuk

int val = 0;  // variable to store the value read
int analogPin = A1;

void setup() {

   Serial.begin(1000000);           //  setup serial
  cli();                      //stop interrupts for till we make the settings
  /*1. First we reset the control register to amke sure we start with everything disabled.*/
  TCCR1A = 0;                 // Reset entire TCCR1A to 0 
  TCCR1B = 0;                 // Reset entire TCCR1B to 0
 
  /*2. We set the prescalar to the desired value by changing the CS10 CS12 and CS12 bits. */    
  TCCR1B |= B00000011;        //Set CS12 to 1 so we get prescalar 64 
  // Frec CLK =16MHz => Tclk=1/16MHz = 62.5ns
  // al setear el preescaler en 64, se divide la frec de clk.
  // Frec preesc=16MHz/64 = 250KHz => Tpreesc=4us
  // Por lo que cada 4us se incrementará en 1 el contador del timer.
  /*3. We enable compare match mode on register A*/
  TIMSK1 |= B00000010;        //Set OCIE1A to 1 so we enable compare match A 
  
  /*4. Set the value of register A to 31250*/
  //OCR1A = 250;             //Finally we set compare register A to this value 
  //OCR1A = 500;             // Para muestrear a 500Hz
  OCR1A = 1388;              // Para muestrear a 180Hz como Fernando Clara
  // Aqui se indica que se dispare una interrupcion cada ver que el contador del timer llegue a 250us
  // 4us*250=1ms por lo que la frec a la que se disparan las interrupciones es de 1kHz
  sei();                     //Enable back the interrupts
}

void loop() {
  
}

//With the settings above, this IRS will trigger each 1ms.
ISR(TIMER1_COMPA_vect){
  
  TCNT1  = 0;                  //First, set the timer back to 0 so it resets for next interrupt 
  val = analogRead(analogPin);  // read the input pin
  envia_trama();

}

void envia_trama() {    // la funcion descompone val en sus digitos y los envia n veces. (al modificar n, se modifica la base de tiempo en Matlab)
  
  // Enviar la trama con 'A' como inicio y 'Z' como final
  Serial.write('A');
  Serial.write((byte)val);
  Serial.write((byte)(val >> 8)); // Enviar el segundo byte del entero (solo si numeroint es mayor a 255)
  Serial.write('Z');
  
}
