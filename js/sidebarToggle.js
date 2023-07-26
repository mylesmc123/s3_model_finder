/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */
function openNav() {
    // document.getElementById("sidebar").style.width = "250px";
    document.getElementById("sidebar").style.visibility = "visible"
    // document.getElementById("map").style.marginLeft = "250px";
    document.getElementById("sidebarheader").innerText = "Layer Groups";
    document.getElementById("sidebaropenbutton").style.visibility = "hidden"
  }

/* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
function closeNav() {
    // console.log( document.getElementsByClassName("sidebar")[1].style);
    // document.getElementById("sidebar").style.width = "0";
    document.getElementById("sidebarheader").innerText = "";
    document.getElementById("sidebaropenbutton").style.visibility = "visible"
    // document.getElementById("map").style.marginLeft = "0";
    document.getElementById("sidebar").style.visibility = "hidden"
  }