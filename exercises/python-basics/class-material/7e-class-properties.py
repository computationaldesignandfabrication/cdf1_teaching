"""Classes"""
# A class a code template for creating objects. Creating a new class creates a new type of object. 
# Using this template, as many instances of that type can be made. Each class instance can have attributes attached to it for maintaining its state.

class Rectangle():
    def __init__(self, length, width):
        self.length = length
        self.width = width
        
    # Class property.
    def get_area(self):
        return self.length * self.width

# Creating an instance of the Rectangle class
my_rectangle = Rectangle(length=2, width=1)

# Printing the rectangle area class property
print("Rectangle area:", my_rectangle.area)
