import MapLibreStyleSwitcherControl from './MapStyleSwitcher.js'
import layerControlSimple from './layerControlSimple.js'
import layerControlGrouped from './layerControlGrouped.js'
import * as Markers from './markers.js'


const apiKey = 'G28Wx0TEh00gRJifwBmD'
  
// https://cloud.maptiler.com/maps/
// https://github.com/maplibre/demotiles
var styles = [
    {
      title: "Topo",
      uri:
        "https://api.maptiler.com/maps/topo-v2/style.json?key=" +
        apiKey,
    },
    {
      title: "Satellite",
      uri:
        "https://api.maptiler.com/maps/hybrid/style.json?key=" +
        apiKey,
    },
    {
      title: "Toner",
      uri:
        "https://api.maptiler.com/maps/toner-v2/style.json?key=" +
        apiKey,
    },
    {
      title: "Voyager",
      uri:
        "https://tiles.basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    },
    {
      title: "Positron",
      uri:
        "https://tiles.basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    },
    {
      "uri": "https://tiles.basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      "title": "Dark Matter"
    },
  ];

  styles.sort((a,b) => (a.title > b.title) ? 1 : ((b.title > a.title) ? -1 : 0))

var map = new maplibregl.Map({
  container: 'map',
  style: 'https://api.maptiler.com/maps/hybrid/style.json?key=' + apiKey, // stylesheet location
  center: [-93.291, 30.8597], // starting position [lng, lat]
  zoom: 7 // starting zoom
  });

map.addControl(new maplibregl.NavigationControl(), 'top-right');

// map.addControl(new MapLibreStyleSwitcherControl(styles, apiKey))

// Create a popup, but don't add it to the map yet.
var popup = new maplibregl.Popup({
  closeButton: false,
  onClick: true

});

var colors = {
  0: '#a6cee3',
  1: '#1f78b4',
  2: '#b2df8a',
  3: '#33a02c',
  4: '#fb9a99',
  5: '#e31a1c',
  6: '#fdbf6f',
  7: '#ff7f00',
  8: '#cab2d6',
}

map.on('style.load', function () {

  fetch(`../output/perimeter_list.json`)
    .then(response => response.json())
    .then(data => {
        // console.log(data);
        var i=0
        data.forEach(element => {
            // console.log(element);
            const layer_name_array = element.split("\\");
            const splitter = layer_name_array[layer_name_array.length - 1];
            const layer_title = splitter.split(".")[0];
            // console.log(layer_title);
            map.addLayer({
              'id': layer_title,
              'type': 'fill',
              "paint": {
                "fill-color": colors[i],
                "fill-opacity": 0.5
              },
              'source': {
                type: "geojson",
                data: element
              }
            });
          if (i<8) {
          i++
          } else {  
            i=0
          };
        })
    })

  map.on('click', function (e) {
    var features = map.queryRenderedFeatures(e.point);
    // console.log(features);
    var displayProperties = [
      'layer',
      'properties',
    ];
    
    var displayFeatures = features.map(function (feat) {
      
      var displayFeat = {};
      
      displayProperties.forEach(function (prop) {
        // console.log(feat);
        displayFeat[prop] = feat[prop];
      });
      
      return displayFeat;
    });

    var wantedPopupData = {};
    
    displayFeatures.forEach(function (feature) {
      
        wantedPopupData[feature.layer.id] = {
          "Model Title": feature.properties["Model Title"],
          "Region": feature.properties["Region"],
          '2D Area':feature.properties.Area2D,
          "Run Type": feature.properties["Run Type"],
          "Timestep": feature.properties["Timestep"],
          "Software Version": feature.properties["Software Version"],
          "Units System": feature.properties["Units System"],
          "S3 Model Location": feature.properties["S3 Model Location"],
        }
        // console.log(Object.values(wantedPopupData).length);
    });

    // Display a popup with the wanted popup data
    if (Object.values(wantedPopupData).length) {
      // console.log(wantedPopupData);
      var popuptext = ''
      Object.entries(wantedPopupData).forEach(entry => {
        const [key, value] = entry;
        // console.log(key, value);
        popuptext = popuptext.concat(`<br><b><u>${key}</u></b><br>
        <b>Model Title</b>: ${value["Model Title"]}<br>
        <b>Region</b>: ${value.Region}<br>                              
        <b>Area2D</b>: ${value.Area2D}<br>
        <b>Run Type</b>: ${value["Run Type"]}<br>
        <b>Timestep</b>: ${value["Timestep"]}<br>
        <b>Software Version</b>: ${value["Software Version"]}<br>
        <b>Units System</b>: ${value["Units System"]}<br>
        <b>S3 Model Location</b>: ${value["S3 Model Location"]}<br>
                                      `)
        // console.log(popuptext);
      });
      // if data is not null, add popup to map
  
      popup.setLngLat(e.lngLat)
          // .setText(JSON.stringify(wantedPopupData).replace(/[{}]/g, '').replace(/"/g, ''))
      .setHTML(popuptext)
      .setMaxWidth("800px")          
      .addTo(map);
      
    }
  }); // end map.on('mousemove')

  map.on('mouseleave', function() {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });

}) // end map.on('load')


  