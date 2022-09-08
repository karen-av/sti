
class Vehicle:
    """docdtring"""

    def __init__(self, color, doors, tires, vtype):
        """constructor"""
        self.color = color
        self.doors = doors
        self.tires = tires
        self.vtype = vtype

    def brake(self):
        """Stop the car"""
        return "%s break" % self.vtype
    
    def drive(self):
        """Drive car"""
        return "i'm drivang a %s %s!" %(self.color, self.vtype)

if __name__ == "__main__":
    car = Vehicle("blue", 5, 4, "car")
    print(car.brake())
    print(car.drive())

    track = Vehicle('red', 3, 6, 'track')
    print(track.tires)