window.Util = {
  makeLocKey: function(lat, lng){
    return lat + "::" + lng;
  },
  getRandomArbitary: function(min, max) {
    return Math.random() * (max - min) + min;
  }
}

Vendor = function(data){
  this.public_profile_url = data.public_profile_url;
  this.display_name = data.display_name;
  this.assignment_status = data.assignment_status;
  this.club_status = data.club_status;
  this.vendor_id = data.vendor_id;
  this.display_location = data.display_location;
  this.lat = data.latitude;
  this.lng = data.longitude;
  this.latLng = new google.maps.LatLng(this.lat, this.lng);
  this.public_photo_url = data.public_photo_url;
  this.is_public = data.is_public;
}

VendorLocation = function(m, vendorData){
  this.mapManager = m;

  var firstVendor = new Vendor(vendorData);
  console.log(firstVendor);
  this.vendors = [firstVendor];
  this.locKey = Util.makeLocKey(firstVendor.lat, firstVendor.lng);
  this.latLng = this.vendors[0].latLng;

  this.image = '/static/images/GBlue.png';
  var markerOptions = {position: this.latLng, optimized: false, icon: this.image};
  this.marker = new google.maps.Marker(markerOptions);
}

VendorLocation.prototype.addVendor = function(vendorData){
  this.vendors.push(new Vendor(vendorData));
}

VendorLocation.prototype.getIWContent = function(){
  return '<div>' +
    'STUFF HERE' +
    '</div>';
}

VendorLocation.prototype.onClick = function(){
  this.mapManager.onMarkerClick(this);
}

VendorLocation.prototype.setMap = function(map){
  this.marker.setMap(map);
  this.map = map;
  if (map)
    this.clickListener = google.maps.event.addListener(this.marker, 'click', _(this.onClick).bind(this));
  else if (this.clickListener)
    google.maps.event.removeListener(this.clickListener);
}



var PlaceMapManager = function(app, map){
  this.app = app;
  this.map = map;
  this.places = [];
  this.infoWindow = new google.maps.InfoWindow();
  google.maps.event.addListener(this.map, 'click', _(function(){this.infoWindow.close()}).bind(this) );
}

PlaceMapManager.prototype.openInfoWindow = function(marker, content){
  this.infoWindow.setContent(content);
  this.infoWindow.open(this.map, marker);
}

PlaceMapManager.prototype.clearMap = function(){
  _(this.places).each( _(function(place){
    place.setMap(null);
  }).bind(this) );
}

PlaceMapManager.prototype.showPlacesFromFullResponse = function(data, p){
  p = p||{};
  if (p.clearMap)
    this.clearMap();

  this.showPlacesInternal(data, p);
}

PlaceMapManager.prototype.showPlacesInternal = function(data, p){
  p = p||{};
  if (data.length){
    var bounds = new google.maps.LatLngBounds();
    _(data).each( _(function(vendorData){


      //XXX for testing with non-geocoded data
      if (!vendorData.latitude) vendorData.latitude = Util.getRandomArbitary(0, 1) -.5 +47.60651025683697;
      if (!vendorData.longitude) vendorData.longitude = Util.getRandomArbitary(0, 1) -.5 -122.33057498931885;
      //XXX



      // either make new vendorLocation or add new vendor to existing vendorLocation
      //(multiple vandors can be at one location -- should share one location marker)
      var existingLocation = _(this.places).find(function(place){ return place.locKey == Util.makeLocKey(vendorData.latitude, vendorData.longitude); });
      if (existingLocation) {
        existingLocation.addVendor(vendorData);
      }
      else {
        var vendorLocation = new VendorLocation(this, vendorData);
        this.places.push( vendorLocation );
        vendorLocation.setMap(this.map);
        if (p.fitMapToMarkers) bounds.extend(vendorLocation.latLng)
      }
    }).bind(this) );
    if (p.fitMapToMarkers) this.map.fitBounds(bounds);
  }
}

PlaceMapManager.prototype.onMarkerClick = function(place){
  this.openInfoWindow(place.marker, place.getIWContent());
  this.selectPlace(place);
}

PlaceMapManager.prototype.selectPlace = function(place){
  // if (this.lastSelected)
  //     this.lastSelected.setHighlight(false);
  //   place.setHighlight(true);
  //   this.lastSelected = place;
  //   this.map.panTo(place.latLng);
}
