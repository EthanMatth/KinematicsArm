#include <Servo.h>
#include <math.h>

#define NUM_SERVOS 6

void serverSetup();
void parseCommand(String input);
void Inverse(float x, float y, float h);
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
  // put your setup code here, to run once:
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
  
  //Inverse(x, y, h);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    parseCommand(input);
    reportPositions();
  }

}

void servoSetup()
{

}

void parseCommand(String input) {
  input.replace(',', ' ');   // Allow commas OR spaces
  input.trim();

  float coords[3];
  int count = 0;

  while (input.length() > 0 && count < 3) {
    int spaceIndex = input.indexOf(' ');

    String val = (spaceIndex == -1) ? input : input.substring(0, spaceIndex);
    val.trim();

    if (val.length() > 0) {
      coords[count] = val.toFloat();   // Convert to float
      count++;
    }

    if (spaceIndex == -1) break;
    input = input.substring(spaceIndex + 1);
  }

  // Must have exactly 3 values (x, y, h)
  if (count == 3) {
    Inverse(coords[0], coords[1], coords[2]);
  } else {
    Serial.println("Error: Expected 3 values (x, y, h)");
  }
}


void Inverse(float x, float y, float h) 
{
  float r = sqrt(pow(x, 2) + pow(y, 2));
  Serial.print("Radius: ");
  Serial.println(r);
  int theta = degrees(atan2(y, x));
  Serial.print("theta1: ");
  Serial.println(theta);

  target[t1] = theta;

  // boolean for if the arm is elbow down
  // Important for futer calculations
  bool elbow_down;
  if (((current[t2] <= 90) && (current[t3] >= 90)) || ((current[t2] > 90) && (current[t3] < 90))) {
    elbow_down = true;
  } else {
    elbow_down = false;
  }

  // Intermediate angles for theta2 and theta3
  int p = sqrt(pow(r, 2) + pow(h, 2));
  int gamma = degrees(acos((pow(L1, 2) + pow(L2, 2) - pow(p, 2))/(2*L1*L2)));
  Serial.print("Gamma: ");
  Serial.println(gamma);
  int alpha = degrees(acos((pow(L1, 2) + pow(p, 2) - pow(L2, 2))/(2*L1*p)));
  Serial.print("Alpha: ");
  Serial.println(alpha);
  int beta = degrees(atan2(h, r));
  Serial.print("Beta: ");
  Serial.println(beta);
  // Calculate theta2 and theta3
  elbow_down = false;
  if(elbow_down)
  {
    target[t2] = beta - alpha;
    target[t3] = 90 - (180 - gamma);
  } 
  else
  {
    target[t2] = beta + alpha;
    target[t3] = 90 + (180 - gamma);
  }

  // Theta 4 and Theta 5: Inverse kinematics using matrix T3_6
  float r12, r32, r21, r23;
  
  // Define the rotation values here
  r12 = -sin(radians(current[t4]));
  r21 = sin(radians(current[t5]));
  r23 = cos(radians(current[t5]));
  r32 = -cos(radians(current[t4]));


  target[t4] = degrees(atan2((-r12 - cos(radians(target[t1]))*sin(radians(target[t2] + target[t3]))), (-r32 - cos(radians(target[t2] + target[t3])))));
  target[t5] = degrees(atan2((r21 - sin(radians(target[t1]))*cos(radians(target[t2] + target[t3]))), (r23 - cos(radians(target[t1])))));

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
