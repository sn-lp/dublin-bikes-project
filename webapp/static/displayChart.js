// function to display the bikes or spaces availability trend chart when the "More" button is clicked
  function displayChart(stationId, stationName) {
    let endpoint;
    if (viewAvailableBikes) {
      endpoint = '/availability_history?stationId=' + stationId;
    }
    else {
      endpoint = '/available_spaces_history?stationId=' + stationId;
    }
      fetch(endpoint)
      .then(response => response.json())
      .then(stationHistory => {
        // each dataset is a day of the week with the avg availability for every hour of the day
        let datasets = [];
        createChartDataset(stationHistory, datasets);
        // create a canvas where the chart will be displayed
        let canvas = document.getElementById('trendChart');
        let ctx = canvas.getContext('2d');
        // the title in the y-axis in the chart will change accordingly with the view that is selected
        let labelTitle;
        if (viewAvailableBikes){
          labelTitle = "Bikes Available"
        }
        else {
          labelTitle = "Free Spaces"
        }
        // create the chart for each dataset and station
        createChart(ctx, datasets, stationName, labelTitle);
        // Get the modal
        let modal = document.getElementById("myModal");
        // show the modal
        modal.style.display = "block";
    })
  };

  function createChartDataset(stationHistory, datasets) {
    // keys will be a list with [0, 1, 2, 3, etc.] -- 0=Monday; 1=Tuesday; etc.
    const keys = Object.keys(stationHistory);
    // dicts to convert the keys that we get from stationAvailabilityHistory into the weekdays and give a color to each of the days for our chart
    let labelsDict = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"};
    let colorsDict = {0: "#622569", 1: "#80ced6", 2: "#ada397", 3: "#e0876a", 4: "#ffcc5c", 5: "#034f84", 6: "#82b74b"};
    for(var i = 0; i < keys.length; i++) {
      let dayDataset = {label: labelsDict[i], data: [], fill: false, borderColor: colorsDict[i]};
      for (var j = 0; j < stationHistory[keys[i]].length; j++) {
        if (viewAvailableBikes){
          dayDataset.data.push(stationHistory[keys[i]][j].availableBikes);
        }
        else {
          dayDataset.data.push(stationHistory[keys[i]][j].freeStands);
        }
      }
      datasets.push(dayDataset);
    }
  };

  function createChart(ctx, datasets, stationName, labelTitle) {
    chart = new Chart(ctx, {
          type: 'line',
          data: {
              datasets: datasets,
              labels: ['0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h', '20h', '21h', '22h', '23h']
          },
          responsive: true,
          maintainAspectRatio: false,
          options: {
            legend: {
              labels: {
                fontSize: 20,
              }
            },
            tooltips: {
              titleFontSize: 20,
              bodyFontSize: 20,
            },
            title: {
                display: true,
                text: stationName,
                fontSize: 30,
            },
            scales: {
              yAxes: [{
                ticks: {
                  fontSize: 22,
                },
                scaleLabel: {
                  display: true,
                  labelString: labelTitle,
                  fontSize: 25,
                }
              }],
              xAxes: [{
                ticks: {
                  fontSize: 20,
                },
                  scaleLabel: {
                    display: true,
                    labelString: 'Hours',
                    fontSize: 25,
                  }
                }]
              },
            }
          },
        )
        // Get the modal
        let modal = document.getElementById("myModal");
        // show the modal
        modal.style.display = "block";
  }