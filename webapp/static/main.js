// by default the selected view on page load is "Available Bikes"
let viewAvailableBikes = true;
let map;
let infowindow;
let markersArray = [];
let chart;
let overlay;

function toggleView() {
  if (viewAvailableBikes) {
    viewAvailableBikes = false;
    document.getElementById("viewButton").innerHTML = "Show Available Bikes";
  } else {
    viewAvailableBikes = true;
    document.getElementById("viewButton").innerHTML = "Show Free Spaces";
  }
  updateMarkers();
  changeViewTitle();
}

function initMap() {
  changeViewTitle();
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.3498, lng: -6.2603 },
    zoom: 13,
  });

  updateMarkers();
}

function updateMarkers() {
  const bounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(53.342271085874636, -6.2620039424284215),
    new google.maps.LatLng(53.349777640548794, -6.252099752008924)
  );

  /**
   * The custom LoadingOverlay object contains the loading gif,
   * the bounds of the image, and a reference to the map.
   * Must be defined inside the updateMarkers function because it requires a
   * reference to google maps API
   */
  class LoadingOverlay extends google.maps.OverlayView {
    constructor(bounds, image) {
      super();
      this.bounds = bounds;
      this.image = loadingGif;
    }
    /**
     * onAdd is called when the map's panes are ready and the overlay has been
     * added to the map.
     */
    onAdd() {
      this.div = document.createElement("div");
      this.div.style.borderStyle = "none";
      this.div.style.borderWidth = "0px";
      this.div.style.position = "absolute";
      // Create the img element and attach it to the div.
      const img = document.createElement("img");
      img.src = this.image;
      img.style.width = "50%";
      img.style.height = "50%";
      img.style.position = "absolute";
      this.div.appendChild(img);
      // Add the element to the "overlayLayer" pane.
      const panes = this.getPanes();
      panes.overlayLayer.appendChild(this.div);
    }
    draw() {
      // We use the south-west and north-east
      // coordinates of the overlay to peg it to the correct position and size.
      // To do this, we need to retrieve the projection from the overlay.
      const overlayProjection = this.getProjection();
      // Retrieve the south-west and north-east coordinates of this overlay
      // in LatLngs and convert them to pixel coordinates.
      // We'll use these coordinates to resize the div.
      const sw = overlayProjection.fromLatLngToDivPixel(
        this.bounds.getSouthWest()
      );
      const ne = overlayProjection.fromLatLngToDivPixel(
        this.bounds.getNorthEast()
      );

      // Resize the image's div to fit the indicated dimensions.
      if (this.div) {
        this.div.style.left = sw.x + "px";
        this.div.style.top = ne.y + "px";
        this.div.style.width = ne.x - sw.x + "px";
        this.div.style.height = sw.y - ne.y + "px";
      }
    }
    /**
     *  Set the visibility to 'hidden' or 'visible'.
     */
    hide() {
      if (this.div) {
        this.div.style.visibility = "hidden";
      }
    }
  }

  // Setup loading symbol
  let loadingGif = "/static/ajax-loader.gif";
  overlay = new LoadingOverlay(bounds, loadingGif);
  overlay.setMap(map);

  // We have one infowindow that is shared between all stations so that only one can be open at a time
  // this closes the infoWindow if one exists already, so when changing to another view an existing infoWindow cannot be carried to that view
  if (infowindow) {
    infowindow.close();
  }
  infowindow = new google.maps.InfoWindow();

  fetch("/stations")
    .then((response) => response.json())
    .then((stationData) => {
      for (const station of stationData) {
        let stationProperty = viewAvailableBikes
          ? station.availableBikes
          : station.freeStands;
        // get the marker colour according to the current selected view
        let colourIcon = getMarkerColour(stationProperty, station.totalStands);
        // this replaces the char `'` with ' ' in the station name when passed to displayChart() because it was causing troubles when clicking the "More" button
        const stationName = station.name.replaceAll("'", " ");
        // get the infoWindow content (number of bikes and free spaces for each station)
        let contentString = getWindowContent(station, stationName);

        // code to create markers the first time the page loads
        // check if all station markers were added to the markersArray, if not it means it is still the first time a station marker is being created
        if (markersArray.length != stationData.length) {
          const newMarker = new google.maps.Marker({
            position: { lat: station.latitude, lng: station.longitude },
            icon: colourIcon,
            map,
          });
          // add the station marker to the array markersArray
          markersArray.push(newMarker);
          newMarker.addListener("click", () => {
            // Close any open info window
            if (infowindow) infowindow.close();
            infowindow.setContent(contentString);
            infowindow.open(map, newMarker);
          });
        } else {
          // this code makes it possible to just update the marker's colours and infoWindow content when changing the view, instead of creating new markers (fixes bug where markers were off after changing views)
          // get marker from markersArray that belongs to the station
          for (marker of markersArray) {
            markerPosition = marker.getPosition();
            markerLat = markerPosition.lat();
            markerLong = markerPosition.lng();
            if (
              markerLat == station.latitude &&
              markerLong == station.longitude
            ) {
              // clear previous listeners to update content string (meanwhile number of bikes/spaces might have changed)
              google.maps.event.clearListeners(marker, "click");
              // update marker colour
              marker.setIcon(
                getMarkerColour(stationProperty, station.totalStands)
              );
              // get updated content for infowindow
              let contentString = getWindowContent(station, stationName);
              google.maps.event.addListener(this.marker, "click", function () {
                // Close any open info window
                if (infowindow) infowindow.close();
                // add the updated content and open the infoWindow
                infowindow.setContent(contentString);
                infowindow.open(this.getMap(), this);
              });
            }
          }
        }
      }
    })
    .then(() => overlay.hide());
}

function changeViewTitle() {
  let viewTitle = document.getElementById("viewTitle");
  if (viewAvailableBikes) {
    viewTitle.textContent = "Viewing Available Bikes";
  } else {
    viewTitle.textContent = "Viewing Free Spaces";
  }
}

function getMarkerColour(stationProperty, totalStands) {
  let colourIcon;
  // Assign different colours to stations based on percentage bike availability
  // The ranges for each colour were decided to ensure an approximately equal
  // number of stations in each group based on historical data
  if (stationProperty / totalStands < 0.26) {
    colourIcon = "/static/red-square.png";
  } else if (stationProperty / totalStands < 0.44) {
    colourIcon = "/static/ylw-square.png";
  } else {
    colourIcon = "/static/grn-square.png";
  }
  return colourIcon;
}

function getWindowContent(station, stationName) {
  // Information displayed in info window (the same in both views)
  let contentString =
    station.name +
    "<ul>" +
    "<li>Available Bikes: " +
    station.availableBikes +
    "</li>" +
    "<li>Free Stands: " +
    station.freeStands +
    "</li>" +
    "</ul>" +
    "<button type='button' id='moreButton' onclick='displayChart(" +
    station.stationId +
    ',"' +
    stationName +
    "\")'>More</button>";
  return contentString;
}
