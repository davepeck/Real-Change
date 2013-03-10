function VendorMapApp(){
  var mapOptions = {
    center: new google.maps.LatLng(47.60651025683697,-122.33057498931885),
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("vendormap"), mapOptions);

  var latLon = new google.maps.LatLng(47.6560, -122.3401);
  var markerOptions = {position: latLon, optimized: false, icon: this.image, map: map};
  var marker = new google.maps.Marker(markerOptions);
  var directionsURL = "https://maps.google.com/maps?daddr=" + latLon.toString();
  var contentString = '<div id="infowin">' +
    '<h1>QFC Wallingford</h1>' +
    '<p><strong>6am - 2pm:</strong> A Real Change vendor sells 300 papers here every month.</p>' +
    '<p><strong>2pm - 10pm:</strong> Matt Lerner sells 300 papers here every month. ' + 
    '<a href="http://realchangenews.org/index.php/site/archives/7252">Read vendor profile</a>.</p>' +
    '<p class="address">QFC Wallingford <br />1801 N 45th St <br />Seattle, WA‎ 98103' +
    '<br /><a href="' + directionsURL + '">Directions</a></p>' +
    '</div>'
  var infoWinOptions = {content: contentString, maxWidth: 300};
  var infoWin = new google.maps.InfoWindow(infoWinOptions);
  infoWin.open(map, marker);


  this.mapManager = new PlaceMapManager(this, map);

  this.fetchVendors();

  //MATT DO STUFF HERE :)

}

VendorMapApp.prototype.fetchVendors = function(){
  var url = '/api/vendors/';
  $.ajax({
    url: url,
    dataType: 'json',
    success: _(function(data){
        console.log("fetch done");
        this.mapManager.showPlacesFromFullResponse(data, {clearMap:true, fitMapToMarkers:true});
      }).bind(this),
    error: _(function(){
        console.log("fetch error");
      }).bind(this)
  });
}
