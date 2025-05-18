// Images
// For Light
let lightOn = "static/Pictures/light-bulb.png"; // ON
let lightOff = "static/Pictures/lightbulb.png"; // OFF
let lightElement = document.getElementById("light");

// For Fan
let fanOn = "static/Pictures/fan-gif-76-blue-fan-moving.gif"; // ON
let fanOff = "static/Pictures/fanOffImg.png"; // OFF
let fanElement  = document.getElementById("fan");

function changeFanImage(is_fan_on)
{
    if (is_fan_on) 
    {
        fanElement.src = fanOn;
    } 
    else 
    {
        fanElement.src = fanOff;
    }
}

// Run these functions on load to initialize all the components on the page
window.onload = function() 
{
    fetchDHT11Data() 
    setInterval(fetchDHT11Data, 5000);
    updateGages()
    setInterval(updateGages, 5000);
    changeFanImage(is_fan_on)
}

// Temperature and humidity gauges
var tempGauge, humidityGauge;

function updateGages() {
    // Look if gauge for temp exists
    if (tempGauge) {
        // If yes, update value
        tempGauge.refresh(temp);
    } else {
        // If no, create new temp gauge
        tempGauge = new JustGage({
            id: "temperature",
            value: temp,
            min: 0,
            max: 50,
            symbol: '°C',
            title: "Temperature",
            gaugeWidthScale: 0.3,
            levelColors: ["#00A2E8", "#00A2E8", "#00A2E8"],
            valueFontColor: ["#858585"]
            // For different colors at different levels
            //levelColors: ["#00A2E8", "#FFD670", "#BC2C1A"]
        });
    }

    // Check if humidity gauge already exist
    if (humidityGauge) {
        // If yes, update value
        humidityGauge.refresh(humidity); 
    } else {
        // If no, create new humidity gauge
        humidityGauge = new JustGage({
            id: "humidity",
            value: humidity,
            min: 0,
            max: 100,
            symbol: '%',
            title: "Humidity",
            gaugeWidthScale: 0.3,
            levelColors: ["#00A2E8", "#00A2E8", "#00A2E8"],
            valueFontColor: ["#858585"]
            // For different colors at different levels
            //levelColors: ["#00A2E8", "#FFD670", "#BC2C1A"]
        });
    }
}

// Get the data received from the dht11 that was put into the dht_data.json file
// Then get the data, and display in the gauges
function fetchDHT11Data() {
    fetch('/static/data/dht_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('An error occurred.');
            }
            return response.json();
        })
        .then(data => {
            const last_measurement = data.measurements[data.measurements.length - 1]; //-1 because starts with 0
            humidity = last_measurement.humidity;
            temp = last_measurement.temp;         

            console.log("temp is " + temp);
            console.log("humidity is: " + humidity);

            updateGages(); // Call method to update gauges
        })
        .catch(error => console.error('Failed to fetch data.', error));
}
