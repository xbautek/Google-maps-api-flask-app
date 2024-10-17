import geocoder

class Location:
    def __init__(self, city=None):
        self.city = city
        self.location = self.get_location()

    def get_location(self):
        if self.city:
            g = geocoder.osm(self.city)
        else:
            g = geocoder.ip('me')
        return g.latlng

    def get_longitude(self):
        return self.location[1]

    def get_latitude(self):
        return self.location[0]
