# IoT-Smart-Home-Hub
Project for 420-531-VA IOT: Internet Of Things

## Project Description
For this project, we were tasked with creating a **smart home system** using a Raspberry Pi, sensors, motors and other components.  

The system is designed to capture environmental data from its surroundings, make decisions based on the collected data, and display the data to a web-based dashboard. 

## Dashboard
Here is the web-based IoT dashboard which displays all the information gathered by the sensors and components attached to the breadboard.  

![IoT-Smart-Home-Hub](https://github.com/user-attachments/assets/163ac591-2931-4b3e-887f-6d7c1a52e530)   

### Capturing of Environmental Data
The smart home system captures **light**, as well as **temperature** and **humidity** data using sensors.

### Decision-Making
A **'*fan*'** (DC motor) and **LED** attached to the breadboard **are turned ON/OFF** depending on whether or not the captured temperature and/or light intensity values exceed the user's preferred threshold values.     

#### *Fan Activation*
If the surrounding temperature is **higher** than the user's preferred temperature, an email is sent to the user asking whether they'd like their fan to be turned on. If the user replies 'yes' to the email, the DC motor will be activated.   

#### *LED Activation*
If the surrounding light intensity is **lower** than the user's preferred light intensity, the LED is turned on and the user is sent an email informing them of the LED's activation.  

### Display
The captured environmental data is displayed onto the web-based dashboard using the [Socket.IO](https://socket.io/) library. The status of the '*fan*' (DC motor) and LED are also displayed, meaning the user can see whether they're ON or OFF.

### Access Control
The system has access control, implemented using Radio Frequency Identification (RFID), which allows it to store user information such as names, and preferences in a database.   
The storing of user preferences allows the smart home to make decisions based on the captured environmental data and the user’s preferences, such as turning a motor on if the surrounding temperature is higher than what the user prefers.
