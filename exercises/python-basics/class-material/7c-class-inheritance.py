"""Classes"""
# A class a code template for creating objects. Creating a new class creates a new type of object. 
# Using this template, as many instances of that type can be made. Each class instance can have attributes attached to it for maintaining its state.

class Rectangle():
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    # Class function.
    def get_area(self):
        return self.length * self.width

# Square class based on the Rectangle class
class Square():
    pass

# Creating an instance of the Square class
my_square = Square(length=2)

print("Square area:", my_square.get_area())