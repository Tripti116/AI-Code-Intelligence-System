class Student:

    def __init__(self, name):
        self.name = name

    def display(self):
        print(self.name)

s = Student("Tripti")
s.display()