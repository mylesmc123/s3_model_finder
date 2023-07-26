import * as mglHelper from "./lib/mglHelpers.js";
import * as domHelper from "./lib/domHelpers.js";

function ToggleLegend(target, map, wantedLayers) {
    // console.log(target);
    // console.log(target.dataset.sourceData);
    // var inputs = target.parentElement.querySelectorAll("[data-master-layer]")
    // console.log(checked);

    // Toggle off any legends
    // document.getElementById("legends").innerHTML = "";
    // document.getElementById("legends").style.display = "none";

    

    // var n_legends = 0

    // map.getStyle().layers.forEach(function (feature) {
    //     // console.log(feature.layout.visibility);
    //     // if (wantedLayers.includes(feature.id) && feature.layout.visibility == true) {
    //     if (wantedLayers.includes(feature.id) && feature.layout.visibility == 'visible') {
    //         console.log(feature.layout.visibility );
    //         n_legends +=1
    //     }
    // });

    // console.log(n_legends);

    // Toggle on "Proposed" scenarios legend
    if (target.id.includes("Proposed") && target.checked == true) {   

        loadJSON(target.dataset.sourceData).then(data => {

            // create a proposed legend div
            var legend_proposed = document.createElement("div")
            legend_proposed.setAttribute("id","legend-proposed")
            // legend_proposed.setAttribute("style","width: 50%;float: left;padding: 2px;margin: 1px")
            legend_proposed.setAttribute("class","column")
            document.getElementById("legends").appendChild(legend_proposed);
            // console.log(document.getElementById("legends"));

            // console.log(data);
            var max = getMax(data, "depth_max")
            var min = getMin(data, "depth_max")
            // console.log(max);
            // console.log(min);
            // create color ramp values
            var rampValues = {
                0: max,
                1: parseFloat((max-min) * 0.75).toFixed(2),
                2: parseFloat((max-min) * 0.5).toFixed(2),
                3: parseFloat((max-min) * 0.25).toFixed(2),
                4: min
            };
            // console.log(rampValues);

            // // create color ramp
            var ramp = document.createElement("dl",{"id":"legendTable-proposed","style":"width: 86px;background: #fff;border: 1px solid #000;padding: 50px 10px;line-height:0px;border-radius:10px;margin-top:10px;"});
            ramp.innerHTML =
                `<dt class="row" style="background:#AB2706;display: inline-block;width:16px;height:16px;"></dt>` +
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">${rampValues[0]}</dd><br>` +
                `<dt class="row" style="background:#C3411C;display: inline-block;width:16px;height:16px;"></dt>` +
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">${rampValues[1]}</dd><br>` +
                `<dt class="row" style="background:#DB5C32;display: inline-block;width:16px;height:16px;"></dt>` +
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">${rampValues[2]}</dd><br>` +
                `<dt class="row" style="background:#F37748;display: inline-block;width:16px;height:16px;"></dt>` +
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">${rampValues[3]}</dd><br>` +
                `<dt class="row" style="background:#FFF70F;display: inline-block;width:16px;height:16px;"></dt>` +
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">${rampValues[4]}</dd><br>`;

            // create header
            var header = document.createElement("h4",{"style":"textAlign: center"});
            header.textContent = `${target.id} Depth (ft)`;
            document.getElementById("legend-proposed").appendChild(header);
            document.getElementById("legend-proposed").appendChild(ramp);

            // turns on legends
            document.getElementById("legends").style.display = "block";
            document.getElementById("legend-proposed").style.display = "block";

        });
        
        

            
        
    // Toggle on "Existing" scenarios legend
    } else if (target.id.includes("Existing") && target.checked == true) {
        

        loadJSON(target.dataset.sourceData).then(data => {

            // create a existing legend div
            var legend_existing = document.createElement("div")
            legend_existing.setAttribute("id","legend-existing")
            legend_existing.setAttribute("class","column")
            // legend_existing.setAttribute("style","width: 50%;float: left;padding: 2px;margin: 1px")
            document.getElementById("legends").appendChild(legend_existing);

            var max = getMax(data, "depth_max")
            var min = getMin(data, "depth_max")
            // console.log(max);
            // console.log(min);
            // create color ramp values
            var rampValues = {
                0: max,
                1: min
            };
            // console.log(rampValues);

            // // create color ramp
            var ramp = document.createElement("dl",{"id":"legendTable-existing","style":"width: 86px;background: #fff;border: 1px solid #000;padding: 50px;line-height:0px;border-radius:10px;margin-top:10px;"});
            ramp.innerHTML =
                `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0">Max: ${rampValues[0]} - Min: ${rampValues[1]}</dd>` +
                `<dd class="row" style="background:#3E6CCE;display: inline-block;width:16px;height:16px;margin-right:4px"></dt>`
                // `<dd class="row" style="display: inline-block;font-size:16px;margin-bottom:0;">Min: ${rampValues[1]}</dd>` +
                // `<dd class="row" style="background:#3E6CCE;display: inline-block;width:16px;height:16px;"></dt>`

            // create header
            var header = document.createElement("h4",{"style":"textAlign: center"});
            header.textContent = `${target.id} Depth (ft)`;
            document.getElementById("legend-existing").appendChild(header);
            document.getElementById("legend-existing").appendChild(ramp);

            // turns on legends
            document.getElementById("legends").style.display = "block";
            document.getElementById("legend-existing").style.display = "block";
            // console.log(document.getElementById("legends"));
        });
    //Toggle off
    } else if (target.id.includes("Proposed") && target.checked == false) {
        // Toggle off "Proposed" scenarios legend
        document.getElementById("legend-proposed").innerHTML = "";
        document.getElementById("legend-proposed").style.display = "none";

    } else if (target.id.includes("Existing") && target.checked == false) {
        document.getElementById("legend-existing").innerHTML = "";
        document.getElementById("legend-existing").style.display = "none";
    }

}

function getMax(json, prop) {
    // console.log(json);
    var max = -10000000;
    for (var i=0 ; i<json.features.length ; i++) {
        
        max = Math.max(parseFloat(json.features[i]["properties"][prop]).toFixed(2), max);
        
        // console.log(max);
    }
    return max;
}

function getMin(json, prop) {
    // console.log(json);
    var min = 10000000;
    for (var i=0 ; i<json.features.length ; i++) {
        
        min = Math.min(parseFloat(json.features[i]["properties"][prop]).toFixed(2), min);
        // console.log(max);
    }
    return min;
}

async function loadJSON (url) {
    const res = await fetch(url);
    return await res.json();
  }

// var maxPpg = getMax(commune.features, "P11_POP");
// alert(maxPpg);

export {
    ToggleLegend
  }