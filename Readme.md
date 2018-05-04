Jonathan Murphy


# Materials used
- RC Chassis
- Esc w/ motor
- Servo
- Raspberry pi
- RC Car Headlight Kit
- Lipo Battery
- USB Battery Bank
- Blinkstick (optional)

# Building instructions

- Connect Motor to ESC
- Connect ESC To Raspberry pi
  - Use pinout.xyz to find the corresponding pins
  - Connect ground to gnd on pi
  - Connect control wire to any BCM slot on the pi
  - Do NOT connect the voltage to the pi
    - In this project we used the battery bank to power the pi
    - Connecting this wire (usually red) can short out the pi or short out the controller if we have both the battery bank and the lipo battery
- Connect Lipo Battery to the ESC. If the ESC doesn't have its on off switch on it, put it on
  - Otherwise the ESC will remain on and drain the battery
- If needed, exchange the drive servo on the chassis and connect it to the pi
  - Use any BCM slot on the pi
- Connect the headlights to any bcm slot on the pi

# Setup the Server

- Make sure pip is installed on your computer
- use pip to install the python3 packages: django, channels, asgi-redis, djangorestframework
- Download the server: https://github.com/MurphyWants/rc-hammer-django
- Rename "rc_server/settings_secret.py.template" to "rc_server/settings_secret.py"
- In "settings_secret.py":
  - In "SECRET_KEY" put in a 50 character secret string using a tool like https://www.miniwebtool.com/django-secret-key-generator/ and then proceed to never give it out to everyone
  - In "ALLOWED_HOSTS" put in all ip addresses and domains that should be accessible to the server
  - Enter in email details used for resetting passwords
- In the file "rc_server/settings.py", in "INSTALLED_APPS" uncomment "rc_car.apps.NullConfig" and comment out "rc_car.apps.RcCarConfig"
- run "python3 manage.py makemigrations"
- Then run "python3 manage.py createsuperuser" to create an admin user
- In the file "rc_server/settings.py", in "INSTALLED_APPS" comment out "rc_car.apps.NullConfig" and uncomment "rc_car.apps.RcCarConfig"
- Provided is an example nginx config file, use something similar to this or an apache equivalent
- run the server with "python3 manage.py runserver 0.0.0.0:80"
- Go to the homepage, click login, login and then create a new car
- Enter in a unique password
- Save the password and uuid for the car client software

# Setup the Client Software

- Install some linux distribution
- install pip
- using pip install the following python3 packages: websocket-client
  - Also install the "blinkstick" package if you're using one
- Download and configure the software
- Found here https://github.com/MurphyWants/rc-hammer-client
- Copy "Setting.py.Template" to "Settings.py"
- Change ESC_Pin to the pin you used to connect the ESC using the BCM values
- Change PWM_Low and PWM_High to the value corresponding to the low and high voltages you intend to give to the ESC
  - This is the lowest value to go back and highest value to go forward
  - My used values are 500 and 2500
- Similar to above, change Steering_Pin to the BCM pin used
- Change Servo_Low and Servo_High similar to above, my used values were 2000 and 2300
  - This is the lowest value to go all the way forward and the highest value to go all the way forward
- Change Server_UUID to the uuid given above
- Change Server_Password to the password given above
- Change headlights pin to the BCM pin used or False
- Change Using_Blinkstick to True if you're using one, False otherwise
- Change domain to the homepage of your website
  - EX: domain.com
- Invert_Motor is an optional value that will invert forward and backward if necessary
- Then just run the main.py file
- Visit the website, visit the page with the car and control it using the buttons, arrow keys or a controller that works with the gamepad.js library
