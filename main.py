from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from functools import partial

CAUGHT = 21
XPLODE = 22

class BombList(Widget):
    pass

class Bomber(Image):
    goal_posn = NumericProperty(0)
    step = NumericProperty(3)
    direction = NumericProperty(-1)
    screen_size = ObjectProperty(None)
    #returns whether it's position is the position it's going to
    def reached_posn(self):
        if abs(self.center_x - self.goal_posn) <= self.step:
            return True
        else:
            return False
    
    #creates a new goal_posn and returns the direction to go in to reach it
    def new_posn(self):
        self.goal_posn = randint(self.width/2, self.screen_size - self.width/2)
        if self.goal_posn < self.center_x:
            self.direction = -1
        else:
           self.direction = 1

    #moves, checks if it's reached it's goal and finds a new one if so
    def move(self):
        self.center_x = self.center_x + self.direction * self.step
        if self.reached_posn():
            self.new_posn()

class Bomb(Image):

    def move(self, bucket):
        print(self.pos)
        self.center_y -= 2
        if self.center_y <= 0:
            print("reached bottom")
            return XPLODE
        elif self.collide_widget(bucket):
            return CAUGHT

class Bucket(Image):
    def move(self, x):
        self.center_x = x


class KaboomGame(Widget):
    bomber = ObjectProperty(None)
    bucket = ObjectProperty(None)
    bombs = ObjectProperty(None)
    pause_button = ObjectProperty(Button())
    score = NumericProperty(0)
    def __init__(self, **kwargs):
        super(KaboomGame, self).__init__()
        self.drop_event = Clock.schedule_interval(self.drop_bomb, 1)
        self.update_event = Clock.schedule_interval(self.update, 1.0/60.0)
        self.pause_event = Clock.schedule_interval(self.pause_game, 10)
        self.pause_button.bind(on_press = self.pause_game)
    def on_touch_down(self, touch):
        self.bucket.move(touch.x)
    def on_touch_move(self, touch):
        self.bucket.move(touch.x)
    def drop_bomb(self, dt):
        self.bombs.add_widget(Bomb(pos=(self.bomber.pos)))
        print("tried to drop a bomb")
    def update(self, dt):
        self.bomber.move()
        for bomb in self.bombs.children[:]:
            res = bomb.move(self.bucket)
            if res == CAUGHT or res == XPLODE:
                self.bombs.remove_widget(bomb)
            elif res == XPLODE:
                print("game over")
                self.bombs.remove_widget(bomb)

    def pause_game(self, dt):
        Clock.unschedule(self.drop_event)
        Clock.unschedule(self.update_event)
            

class KaboomApp(App):
    
    def pause(self, dt, *args):
        for event in args:
            Clock.unschedule(event)
    
    def resume(self, dt, *evnt):
        return Clock.schedule_interval(evnt, freq)

    def build(self):
        game = KaboomGame()
        # Clock.schedule_interval(game.drop_bomb, 1)
        # drop = Clock.schedule_interval(game.update, 1.0/60.0)
        # Clock.schedule_interval(partial(self.pause, drop), 7)
        # Clock.schedule_interval(partial(self.resume, game.drop_bomb), 9)
        return game
    


if __name__ == '__main__':
    KaboomApp().run()
