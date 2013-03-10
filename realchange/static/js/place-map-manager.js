//Friend class Place:
var VendorLocation = function(m, data, opts){
  this.mapManager = m;
  opts = opts||{};

  this.vendor_id = data.vendor_id;
  this.badge = data.badge;
  this.name = data.name;
  this.is_public = data.is_public;
  this.club_status = data.club_status;
  this.assignment_status = data.assignment_status;
  this.lat = data.lat;
  this.lng = data.lng;
  this.latLng = new new google.maps.LatLng(this.lat, this.lng);
  this.photo_url = data.photo_url;

  this.image = '/images/places/pin/'+p.icon+'.png';
  var markerOptions = {position: this.latLng, optimized: false, icon: this.image};
  this.marker = new google.maps.Marker(markerOptions);
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



//End Friend class Place:

var PlaceMapManager = function(p){
  this.app = app;
  this.places = [];
  this.eidPlaces = []; //places by external ID -- keep track of what's shown
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
  p = p||{};
  if (data.length){
    var bounds = new google.maps.LatLngBounds();
    _(data).each( _(function(vendorData){
      // either make new vendorLocation or add new vendor to existing vendorLocation
      //(multiple vandors can be at one location -- should share one location marker)
      var sharesLocation = _(this.places).find(function(place){ return vendorData.lat = place.lat && vendorData.lng = place.lng; });
      if (sharesLocation) {
        sharesLocation.addVendor(vendorData);
      }
      else {
        var vendorLocation = new VendorLocation(this, vendorData, p);
        this.places.push( place );
        place.setMap(this.map);
        if (p.fitMapToMarkers) bounds.extend(place.latLng)
      }
    }).bind(this) );
    if (p.fitMapToMarkers) this.map.fitBounds(bounds);
  }
}

PlaceMapManager.prototype.setMarkerClickHandler = function(f){
  this.markerClickHandler = f;
}

PlaceMapManager.prototype.onMarkerClick = function(place){
  if (this.markerClickHandler)
    this.markerClickHandler(place);
  this.selectPlace(place);
}

PlaceMapManager.prototype.selectPlace = function(place){
  if (this.lastSelected)
    this.lastSelected.setHighlight(false);
  place.setHighlight(true);
  this.lastSelected = place;
  this.map.panTo(place.latLng);
}
