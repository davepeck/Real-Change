function VendorMapApp(){
  var mapOptions = {
    center: new google.maps.LatLng(47.60651025683697,-122.33057498931885),
    zoom: 12,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("vendormap"), mapOptions);

  this.mapManager = new PlaceMapManager(this, map);

  this.fetchVendors();
}

VendorMapApp.prototype.fetchVendors = function(){
  var url = '/api/vendors/';
  $.ajax({
    url: url,
    dataType: 'json',
    success: _(function(data){
        this.mapManager.showPlacesFromFullResponse(data, {clearMap:true, fitMapToMarkers:true});
      }).bind(this),
    error: _(function(){
      }).bind(this)
  });
}
