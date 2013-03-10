function VendorMapApp(){
  var mapOptions = {
    center: new google.maps.LatLng(47.60651025683697,-122.33057498931885),
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("vendormap"), mapOptions);

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
