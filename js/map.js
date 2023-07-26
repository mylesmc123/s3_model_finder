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

// fetch('../config/mapStyles.json')
// .then(response => response.json())
// .then(data => console.log(Object.values(data)))
// // .then(data => data.sort((a,b) => (a.title > b.title) ? 1 : ((b.title > a.title) ? -1 : 0)))
// .then(data => map.addControl(new MapLibreStyleSwitcherControl(Object.values(data), apiKey)))
// .catch(error => console.log(error));

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

  

  // var config = {
  //   collapsed: false,
  //   // Layer order shows up in reverse on page display
  //   layers: [
      
  //     {
  //       id: "100yr Proposed",
  //       hidden: false,
  //       parent: '100yr Proposed',
  //       group: " ",
  //       directory: "100 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "100yr Proposed",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/100yr Proposed_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //     {
  //       id: "100yr Existing",
  //       hidden: false,
  //       parent: '100yr Existing',
  //       group: " ",
  //       directory: "100 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "100yr Existing",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/100yr Existing_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //     {
  //       id: "10yr Proposed",
  //       hidden: false,
  //       parent: '10yr Proposed',
  //       group: " ",
  //       directory: "10 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "10yr Proposed",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/10yr Proposed_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //     {
  //       id: "10yr Existing",
  //       hidden: false,
  //       parent: '10yr Existing',
  //       group: " ",
  //       directory: "10 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "10yr Existing",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/10yr Existing_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //     {
  //       id: "2yr Proposed",
  //       hidden: false,
  //       parent: '2yr Proposed',
  //       group: " ",
  //       directory: "2 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "2yr Proposed",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/2yr Proposed_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //     {
  //       id: "2yr Existing",
  //       hidden: false,
  //       parent: '2yr Existing',
  //       group: " ",
  //       directory: "2 Year Storm Event",
  //       metadata: {
  //         source: {
  //           id: "2yr Existing",
  //           type: "geojson",
  //           data: "../data/westPark/tooltip_layers/2yr Existing_tooltip.geojson"
  //         },
  //         lazyLoading: true
  //       }
  //     },
  //   ]
  // }

  // var wantedLayers = ['2yr Proposed', '2yr Existing', '100yr Proposed', '100yr Existing', '10yr Proposed', '10yr Existing'];

  // const layerControl = new layerControlGrouped(config, wantedLayers);
  // document.querySelector('.sidebar').appendChild(layerControl.onAdd(map));

  map.on('click', function (e) {
    var features = map.queryRenderedFeatures(e.point);
    // console.log(features);
    // Limit the number of properties we're displaying for
    // legibility and performance
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

    
    // var wantedLayers = [];
    var wantedPopupData = {};
    
    displayFeatures.forEach(function (feature) {
      
      // if (wantedLayers.includes(feature.layer.id)) {
        // console.log(feature);
        wantedPopupData[feature.layer.id] = {
          "Model Title": feature.properties["Model Title"],
          "Region": feature.properties["Region"],
          '2D Area':feature.properties.Area2D,
          "Run Type": feature.properties["Run Type"],
          "Timestep": feature.properties["Timestep"],
          "Software Version": feature.properties["Software Version"],
          "Units System": feature.properties["Units System"],
          "S3 Model Location": feature.properties["S3 Model Location"],
          // 'Depth':feature.properties.depth_max,
          // 'Elevation':feature.properties.min_elev,
        }
        // console.log(Object.values(wantedPopupData).length);
        
      // }

    });

    // Display a popup with the wanted popup data
    if (Object.values(wantedPopupData).length) {
      // console.log(wantedPopupData);
      var popuptext = ''
      Object.entries(wantedPopupData).forEach(entry => {
        const [key, value] = entry;
        // console.log(key, value);
        popuptext = popuptext.concat(`<br><b><u>${key}</u></b><br>
                                      Model Title: ${value["Model Title"]}<br>
                                      Region: ${value.Region}<br>                              
                                      Area2D: ${value.Area2D}<br>
                                      Run Type: ${value["Run Type"]}<br>
                                      Timestep: ${value["Timestep"]}<br>
                                      Software Version: ${value["Software Version"]}<br>
                                      Units System: ${value["Units System"]}<br>
                                      S3 Model Location: ${value["S3 Model Location"]}<br>
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

  // When a click event occurs on a feature in the places layer, open a popup at the
  // location of the feature, with description HTML from its properties.
  // map.on('click', 'timeseries', function (e) {

  //   // remove any existing popups
  //   const popups = document.getElementsByClassName("maplibregl-popup");
  //   // const plots = document.getElementById("plotlyPlot");

  //   if (popups.length) {
  //       popups[0].remove();
  //   }
  //   // try {
  //   //   if (plots.length) {
  //   //     plots[0].remove();
  //   //   }
  //   // } catch (error) {
      
  //   // }

  //   var coordinates = e.features[0].geometry.coordinates.slice();
  //   var name = e.features[0].properties.Name;
      
  //   while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
  //   coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
  //   }
  //   console.log(coordinates);
  //   new maplibregl.Popup({className: "plotly-popup"})
  //   .setLngLat(coordinates)
  //   // add div to DOM before creating plotly plot
  //   .setHTML('<div id="plotlyPlot"/>')
  //   // .setContent(Popup.content {wid
  //   .addTo(map);
    
  //   // get timeseries json data
  //   fetch(`../data/westPark/timeseries/timeseries.json`)
  //   .then(response => response.json())
  //   .then(data => {
  //     // console.log(data)
  //     // console.log(Object.keys(data));
  //     // for each event, create plotly trace
  //     var tracedata = [];
  //     Object.keys(data).forEach(key => {
  //       // console.log(key, data[key]);
  //       var values = data[key][name].map(d => d.values);
  //       var times = data[key][name].map(d => d.datetime);
  //       // console.log(times);
  //       var trace =
  //         {
  //           x: times,
  //           y: values,
  //           yaxis: 'WSE (ft)',
  //           type: 'scatter',
  //           name: key
  //         }
  //       ;
  //       tracedata.push(trace)
  //     });
  //     // console.log(tracedata);
  //     var layout = {
  //       title: {
  //         text: name,
  //         xref: 'paper',
  //         x: 0.05,
  //       },
  //       xaxis: {
  //         title: {
  //           text: 'Date',
  //           },
  //       },
  //       yaxis: {
  //         title: {
  //           text: 'WSE (ft)',
  //         }
  //       }
  //     };
  //     Plotly.newPlot('plotlyPlot', tracedata, layout);

  //     // });
    
  //   // var values = data.map(d => d.values);
  //   // var times = data.map(d => d.datetime);
  //   // console.log(times);
  //   // // create plot
  //   // var data = [
  //   //   {
  //   //     x: times,
  //   //     y: values,
  //   //     type: 'scatter'
  //   //   }
  //   // ];
    
  //   });

  // });


  // Store all added markers to be able remove them later
  // var marker_list = [];

  // fetch('../data/westPark/Timeseries_Locations.geojson').then(response => response.json()).then(places => {
  //   marker_list = showGeoJSONPoints(places);
  // });

}) // end map.on('load')

// function showGeoJSONPoints(geojson) {

//   // if (markers.length) {
//   //   markers.forEach(marker => marker.remove());
//   var  markers = [];
//   // }

//   // each feature contains 1 place
//   geojson.features.forEach((feature, index) => {
//     console.log(feature);
    
//     // create icon
//     var markerIcon = document.createElement('div');
//     markerIcon.classList.add("my-marker");
//     // Icon size: 31 x 46px, shadow adds: 4px
//     markerIcon.style.backgroundImage = `url(https://api.geoapify.com/v1/icon/?type=awesome&color=%233f99b1&text=${index + 1}&noWhiteCircle&apiKey=2dd96c68f3bc4562b6d8365176dbaffb)`;
//     // markerIcon.style.backgroundImage = '../data/img/bluepin.png';
//     console.log(markerIcon);

//     var marker_popup = new maplibregl.Popup({
//         anchor: 'bottom',
//         offset: [0, -42] // height - shadow
//       })
//       .setText(feature.properties.Name);

//     var marker = new maplibregl.Marker(markerIcon, {
//         anchor: 'bottom',
//         offset: [0, 4] // shadow
//       })
//       .setLngLat(feature.geometry.coordinates)
//       // .setPopup(marker_popup)
//       .addTo(map);

//     markers.push(marker);
//     console.log(marker);
//   });
//   return markers
// };


  