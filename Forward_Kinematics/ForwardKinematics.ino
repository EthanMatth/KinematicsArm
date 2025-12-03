#include <Servo.h>
#include <math.h>

#define NUM_SERVOS 6

void parseCommand(String input);
void moveServos();
void reportPositions();

Servo servos[NUM_SERVOS];

int servoPins[] = {2, 3, 4, 5, 6, 7};
int current[] = {90, 90, 90, 90, 90, 90};
int target[] = {90, 90, 90, 0, 90, 0};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  for(int i = 0; i < NUM_SERVOS; i++)
  {
    servos[i].attach(servoPins[i]);
    servos[i].write(current[i]);
  }
  delay(500);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    parseCommand(input);
    moveServos();
    reportPositions();
    
  }

}

void parseCommand(String input) {
  input.replace(',', ' ');
  int idx = 0;

  while (input.length() > 0 && idx < NUM_SERVOS) {
    int spaceIndex = input.indexOf(' ');
    String val = (spaceIndex == -1) ? input : input.substring(0, spaceIndex);
    val.trim();

    if (val.length() > 0) {
      target[idx] = constrain(val.toInt(), 0, 180);
      idx++;
    }

    if (spaceIndex == -1) break;
    input = input.substring(spaceIndex + 1);
  }
}

void moveServos()
{
  bool moving = true;

  while(moving) 
  {
    moving = false;

    for (int i = 0; i < NUM_SERVOS; i++) {
      if (current[i] != target[i]) {
        moving = true;

        if (current[i] < target[i]) current[i]++;
        else current[i]--;

        servos[i].write(current[i]);
      }
    }
    delay(25);
  }
}

void reportPositions() 
{
  Serial.print("Current positions: ");
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.print(current[i]);
    if (i < NUM_SERVOS - 1) Serial.print(" ");
  }
  
  Serial.println();
  Serial.print("OK");
  Serial.println();
}

