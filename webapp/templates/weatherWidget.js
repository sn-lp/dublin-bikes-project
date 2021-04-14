// declare openweather API key from config via routes
var KEY = "{{ openweather_api }}";

// create array with parameters
window.myWidgetParam ? window.myWidgetParam : (window.myWidgetParam = []);
window.myWidgetParam.push({
  id: 14,
  cityid: "2964574",
  appid: KEY,
  units: "metric",
  containerid: "openweather-widget",
});

// https://openweathermap.org/widgets-constructor
// creates element specified by tag name 'script'
var script = document.createElement("script");
script.async = true;
script.charset = "utf-8";
script.src =
  "//openweathermap.org/themes/openweathermap/assets/vendor/owm/js/weather-widget-generator.js";
// gets element with the tag name 'script'
var s = document.getElementsByTagName("script")[0];
s.parentNode.insertBefore(script, s);
