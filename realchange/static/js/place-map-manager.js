window.Util = {
  makeLocKey: function(lat, lng){
    return lat + "::" + lng;
  }
}

Vendor = function(data){
  this.vendor_id = data.vendor_id;
  this.badge = data.badge;
  this.name = data.name;
  this.club_status = data.club_status;
  this.assignment_status = data.assignment_status;
  this.lat = data.lat;
  this.lng = data.lng;
  this.latLng = new new google.maps.LatLng(this.lat, this.lng);
  this.photo_url = data.photo_url;
}



VendorLocation = function(m, vendorData){
  this.mapManager = m;

  var firstVendor = new Vendor(vendorData);
  this.vendors = [firstVendor];
  this.locKey = Util.makeLocKey(firstVendor.let, firstVendor.lng);
  this.latlng = this.vendors[0].latlng;

  this.image = '/images/places/pin/'+p.icon+'.png';
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
  this.map = map
  if (map)
    this.clickListener = google.maps.event.addListener(this.marker, 'click', _(this.onClick).bind(this));
  else if (this.clickListener)
    google.maps.event.removeListener(this.clickListener);
}



var PlaceMapManager = function(app, map){
  this.app = app;
  this.map = map;
  this.places = [];
}

PlaceMapManager.prototype.start = function(app){
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
  console.log("show places internal");
  p = p||{};
  if (data.length){
    var bounds = new google.maps.LatLngBounds();
    _(data).each( _(function(vendorData){
      // either make vendorLocation or add new vendor to existing vendorLocation
      //(multiple vandors can be at one location -- should share one location marker)
      var existingLocation = _(this.places).find(function(place){ return vendorData.lat = place.lat && vendorData.lng = place.lng; });
      if (existingLocation) {
        console.log("...adding to existing place");
        existingLocation.addVendor(vendorData);
      }
      else {
        console.log("add new place");
        var vendorLocation = new VendorLocation(this, vendorData);
        this.places.push( place );
        place.setMap(this.map);
        if (p.fitMapToMarkers) bounds.extend(place.latLng)
      }
    }).bind(this) );
    if (p.fitMapToMarkers) this.map.fitBounds(bounds);
  }
}

PlaceMapManager.prototype.onMarkerClick = function(place){
  this.infoWindow.setContent(place.getIWContent);
  this.infoWindow.open(this.map,place.marker);
  this.selectPlace(place);
}

PlaceMapManager.prototype.selectPlace = function(place){
  // if (this.lastSelected)
  //     this.lastSelected.setHighlight(false);
  //   place.setHighlight(true);
  //   this.lastSelected = place;
  //   this.map.panTo(place.latLng);
}
