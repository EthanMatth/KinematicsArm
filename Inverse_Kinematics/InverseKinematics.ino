#include <Servo.h>
#include <math.h>

#define NUM_SERVOS 6

void parseCommand(String input);
void Inverse(float x, float y, float z, float alpha, float beta, float gamma, int claw);
void moveServos();
void reportPositions();

Servo servos[NUM_SERVOS];
enum theta { t1, t2, t3, t4, t5, t6 };

int servoPins[] = {2, 3, 4, 5, 6, 7};
int current[] = {90, 90, 90, 0, 90, 0};
int target[] = {90, 90, 90, 0, 90, 0};

float L1 = 5.0;
float L2 = 3.5;

void setup() {
  Serial.begin(9600);

  for(int i = 0; i < NUM_SERVOS; i++)
  {
    servos[i].attach(servoPins[i]);
    servos[i].write(current[i]);
  }
  delay(500);

  float x = 1;
  float y = 1;
  float h = 2;
 
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    parseCommand(input);
    reportPositions();
  }

}


void parseCommand(String input) {
  input.replace(',', ' ');  // allow commas
  input.trim();

  float vals[7];
  int count = 0;

  // -------- Parse 7 values --------
  while (input.length() > 0 && count < 7) {
    int spaceIndex = input.indexOf(' ');
    String val = (spaceIndex == -1) ? input : input.substring(0, spaceIndex);
    val.trim();

    if (val.length() > 0) {
      vals[count] = val.toFloat();
      count++;
    }

    if (spaceIndex == -1) break;
    input = input.substring(spaceIndex + 1);
  }

  if (count != 7) {
    Serial.println("Error: Expected 7 values: x y z alpha beta gamma claw");
    return;
  }

  float x = vals[0];
  float y = vals[1];
  float z = vals[2];
  float alpha = vals[3];
  float beta  = vals[4];
  float gamma = vals[5];
  int claw    = (int)vals[6];

  Inverse(x, y, z, alpha, beta, gamma, claw);
  
}

void Inverse(float x, float y, float z, float alpha, float beta, float gamma, int claw)
{
  // Calculation for theta 1
  float r = sqrt(pow(x, 2) + pow(y, 2));
  int theta = degrees(atan2(y, x));

  target[t1] = theta;

  // Intermediate angles for theta2 and theta3
  int p = sqrt(pow(r, 2) + pow(z, 2));
  int c = degrees(acos((pow(L1, 2) + pow(L2, 2) - pow(p, 2))/(2*L1*L2)));
  int a = degrees(acos((pow(L1, 2) + pow(p, 2) - pow(L2, 2))/(2*L1*p)));
  int b = degrees(atan2(z, r));
  // Calculate theta2 and theta3

  target[t2] = b + a;
  target[t3] = 90 + (180 - c);
  
  // Rotation values
  float r31 = -sin(radians(target[t2] + target[t3]));
  float r11 = cos(radians(target[t1])) * cos(radians(target[t2] + target[t3]));
  float r21 = sin(radians(target[t1])) * cos(radians(target[t2] + target[t3]));
  float r22 = -sin(radians(target[t1])) * sin(radians(target[t2] + target[t3]));
  float r33 = 0;
  float r12 = -cos(radians(target[t1])) * sin(radians(target[t2] + target[t3]));

  float alpha_2;
  float beta_2;
  float gamma_2;

  if(r31 == 1) 
  {
    beta_2 = -M_PI / 2;
    alpha_2 = 0;
    gamma_2 = -atan2(r12, r22);
  }
  else if(r31 == -1)
  {
    beta_2 = M_PI / 2;
    alpha_2 = 0;
    gamma_2 = atan2(r12, r22);
  }
  else
  {
    beta_2 = atan2(-r31, sqrt(pow(r11, 2) + pow(r21, 2)));
    alpha_2 = atan2(r21, r11);
    gamma_2 = M_PI / 2;
  }

  float alpha_6 = radians(alpha) - alpha_2;
  float beta_6 = radians(beta) - beta_2;
  float gamma_6 = radians(gamma) - gamma_2;

  target[t4] = -degrees(atan((cos(alpha_6) * sin(beta_6) * sin(gamma_6) - sin(alpha_6) * cos(gamma_6)) / (sin(beta_6) * sin(gamma_6))));
  target[t5] = degrees(atan((sin(alpha_6) * cos(beta_6)) / (sin(alpha_6) * sin(beta_6) * cos(gamma_6 - cos(alpha_6) * sin(gamma_6)))));

  // Open and Close Claw
  if(claw) target[t6] = 180;
  else target[t6] = 90;

  moveServos();

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
    delay(20);
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
