
function showGeoJSONPoints(geojson, markers) {

  if (markers.length) {
    markers.forEach(marker => marker.remove());
    markers = [];
  }

  // each feature contains 1 place
  geojson.features.forEach((feature, index) => {
    var markerIcon = document.createElement('div');
    markerIcon.classList.add("my-marker");
    // Icon size: 31 x 46px, shadow adds: 4px
    markerIcon.style.backgroundImage = `url(https://api.geoapify.com/v1/icon/?type=awesome&color=%233f99b1&text=${index + 1}&noWhiteCircle&apiKey=${myAPIKey})`;

    var popup = new Popup({
        anchor: 'bottom',
        offset: [0, -42] // height - shadow
      })
      .setText(feature.properties.name);

    var marker = new Marker(markerIcon, {
        anchor: 'bottom',
        offset: [0, 4] // shadow
      })
      .setLngLat(feature.geometry.coordinates)
      .setPopup(popup)
      .addTo(map);

    markers.push(marker);
  });
  return markers
}