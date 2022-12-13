from random import randint
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import *

class TrendCurve(BoxLayout):
    def __init__(self, **kwargs):
        super(TrendCurve, self).__init__(**kwargs)
        #self size and position
        self.size = (1000, 500)

        self.pos = (60,1)#((Window.width / 2) - ((self.size[0] / 2) - 80) , (Window.height / 2) - (self.size[1] / 2))
        self.text = ""

        self.number_labels = {}
        #This is the point where the trend starts
        self.point_zero = (self.pos[0] + 10, self.pos[1] + 10)
        self.point_zero_x =  self.pos[0] + 10
        self.point_zero_y =  self.pos[1] + 10

        #Points for drawing the line around the rectangle
        #"border line"
        self.x1 = self.pos[0] - 50
        self.y1 = self.pos[1]
        self.x2 = self.pos[0] - 50
        self.y2 = self.pos[1] + self.size[1]
        self.x3 = self.pos[0] + self.size[0]
        self.y3 = self.y2
        self.x4 = self.x3
        self.y4 = self.pos[1]
        self.x5 = self.pos[0] - 50
        self.y5 = self.y4
        self.box_points = [self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, self.x4, self.y4, self.x5, self.y5]

        #Trend line
        self.trend_points = []
        #Trend starts at point zero
        self.trend_points = [self.point_zero_x, self.point_zero_y]
        #Variable for setting resolution of points and numbers
        self.resolution = 10
        #Lines for x and y on the trend.
        self.xline_points = [self.pos[0] + 10, self.pos[1] + 10, self.pos[0] + 10, (self.pos[1] + self.size[1] - 10)]
        self.yline_points = [self.pos[0] + 10, self.pos[1] + 10, (self.pos[0] + self.size[0] - 10), self.pos[1] + 10]

        self.pointlinesx = {}
        self.pointlinesy = {}
        self.r = 0
        self.g = 1
        self.b = 0


        #This is the resolution for how far forward we go for each update that comes.
        self.x_update = 1

        #This is to be rendered before
        with self.canvas.before:
            Color(0.4, 0.4, 0.4, 1)
            self.rectangle = Rectangle(size=self.size, pos=self.pos)
            self.left_addon_rectangle = Rectangle(size=(50, self.size[1]), pos=(self.pos[0] - 50, self.pos[1]))

        #This is the main canvas
        with self.canvas:
            Color(0.2, 0.2, 0.2)
            self.box = Line(points=self.box_points, width=1)
            Color(1, 1, 1)
            self.xline = Line(points=self.xline_points)
            self.yline = Line(points=self.yline_points)


            #These are the small lines for value_y, changing color as it goes upwards
            #red gets more powerful and green gets less powerful
            for i in range(0, self.size[1] - self.resolution, self.resolution):

                if self.r < 1:
                    self.r += 0.03
                if self.g > 0:
                    self.g -= 0.04

                Color(self.r,self.g, 0)

                if i >= 20:
                    self.pointlinesx[i] = Line(points=(self.point_zero_x - 3, self.point_zero_y + i, self.point_zero_x + 3, self.point_zero_y + i), width=0.8)

                    self.number_labels[i] = Label(size=(50, 20),font_size= 8, pos=(self.point_zero_x - 40, (self.point_zero_y + i) - 10), text=str(0 + i))

                self.top_label = Label(text=self.text, size=(100, 50), pos=(self.center[0] - 50, self.center[1] + (self.size[1] / 2) - 50))
                self.ms_label = Label(text="ms", size=(100,50), font_size= 11, pos=(self.point_zero_x - 90, self.point_zero_y + (self.size[1] / 2) - 25))
            #These are the small lines for value_x, only white colored.
            Color(1,1,1)
            for i in range(0, self.size[0], 20):
                if i >= 20:
                    self.pointlinesy[i] = Line(points=(self.point_zero_x + i, self.point_zero_y - 3, self.point_zero_x + i, self.point_zero_y + 3), width=0.8)

        #This is to be rendered after
        with self.canvas.after:
            Color(0.3,0.6,1)
            self.trend = Line(points=self.trend_points, width=0.8)


    def add_points_test(self, dt):
        new_num = randint(50, 200)
        self.add_point(new_num)

    def update(self):
        self.trend.points = self.trend_points

    def add_point(self, y):
        try:
            y = int(y)
        except ValueError:
            pass

        if type(y) == int:
            #The x is updated x pixels forth at a time
            x = self.trend_points[len(self.trend_points) - 2] + self.x_update
            self.trend_points.append(x)

            #y must be between max and min
            if y < 500 > 0:
                self.trend_points.append(self.point_zero_y + y)

            if y > 500:
                self.trend_points.append(500)

            if y < 0:
                self.trend_points.append(0)

            if x > (self.rectangle.size[0] - 10):

                new_point_list = []
                count = 0

                for i in self.trend_points:
                    if (count % 2) != 1:
                        i -= self.x_update

                    new_point_list.append(i)
                    count += 1

                del (new_point_list[0])
                del (new_point_list[1])
                new_point_list[0] = self.point_zero_x + 20

                self.trend_points = new_point_list

        self.update()