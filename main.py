from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
from functools import partial
import kivy

CAUGHT = 21
XPLODE = 22


class BombList(Widget):
    pass


class Bomber(Image):
    goal_posn = NumericProperty(0)
    step = NumericProperty(3)
    direction = NumericProperty(-1)
    screen_size = ObjectProperty(None)

    # returns whether it's position is the position it's going to
    def reached_posn(self):
        if abs(self.center_x - self.goal_posn) <= self.step:
            return True
        else:
            return False

    # creates a new goal_posn and returns the direction to go in to reach it
    def new_posn(self):
        self.goal_posn = randint(self.width/2, self.screen_size - self.width/2)
        if self.goal_posn < self.center_x:
            self.direction = -1
        else:
            self.direction = 1

    # moves, checks if it's reached it's goal and finds a new one if so
    def move(self):
        self.center_x = self.center_x + self.direction * self.step
        if self.reached_posn():
            self.new_posn()


class PauseButton(Button):
    def __init__(self, **kwargs):
        super(PauseButton, self).__init__()

    def on_touch_down(self, touch):
        return True


class Bomb(Image):

    def move(self, bucket, step):
        self.center_y -= step
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
    pause_button = ObjectProperty(None)
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(KaboomGame, self).__init__()
        self.drop_interval = 1
        self.pause_button.bind(on_press=self.pause_game)
        self.paused = False
        self.bombStep = 2
        self.pauses_left = 3
        self.exploding = False
        self.lives = 3
        self.score = 0
        self.began = False

    def begin(self):
        print("in begin")
        self.began = True
        self.drop_event = Clock.schedule_interval(
            self.drop_bomb, self.drop_interval)
        self.update_event = Clock.schedule_interval(self.update, 1.0/60.0)
        self.speedup_event = Clock.schedule_interval(self.speedup, 5)

    def speedup(self, dt):
        if self.paused == False:
            if self.bomber.step < 15:
                self.bomber.step += 0.5
            if self.drop_interval > 0.1:
                self.drop_interval -= 0.05
            if self.bombStep < 10:
                self.bombStep += 0.2
            self.drop_event.timeout = self.drop_interval
            print("drop interval")
        return

    def on_touch_down(self, touch):
        if self.began:
            if self.exploding == False:
                if self.pause_button.collide_point(touch.x, touch.y):
                    if not self.paused:
                        self.pause_game()
                        self.pause_button.text = "Resume"
                        self.pauses_left -= 1
                        self.paused = True
                    else:
                        self.resume_game(0)
                        if not self.pauses_left:
                            self.remove_widget(self.pause_button)
                            return
                        self.pause_button.text = "Pause (" + \
                            str(self.pauses_left) + ")"
                        self.paused = False
                else:
                    self.bucket.move(touch.x)
        else:
            print("should begin")
            self.bucket.move(touch.x)
            self.begin()

    def on_touch_move(self, touch):
        self.bucket.move(touch.x)

    def drop_bomb(self, dt):
        self.bombs.add_widget(Bomb(pos=(self.bomber.pos)))
        print("tried to drop a bomb")

    def update(self, dt):
        self.bomber.move()
        for bomb in self.bombs.children[:]:
            res = bomb.move(self.bucket, self.bombStep)
            if res == CAUGHT:
                self.bombs.remove_widget(bomb)
                self.score += 1
            elif res == XPLODE:
                self.exploding = True
                self.lives -= 1
                print("game over")
                self.pause_game()
                Clock.schedule_once(partial(self.explode_bombs, 0), 0)
                # self.restart_level()

    # Unschedules and reschedules the dropping of bombs to account for new values
    def reschedule(self):
        self.pause_game()
        self.resume_game(0)

    def resume_game(self, dt):
        print("resumed")
        self.drop_event = Clock.schedule_interval(
            self.drop_bomb, self.drop_interval)
        self.update_event = Clock.schedule_interval(
            self.update, 1.0/60.0)
        self.paused = False

    # Unschedules the dropping of bombs and update (moving of bomber and bombs)
    def pause_game(self):
        print("paused")
        self.drop_event.cancel()
        self.update_event.cancel()
        self.paused = True

    def explode_bombs(self, ind, dt):
        print("len of bombs: " + str(len(self.bombs.children)) +
              "\nTrying to index: " + str(len(self.bombs.children) - 1 + ind))
        index = len(self.bombs.children) - 1 + ind
        bomb = self.bombs.children[index]
        bomb.source = "img/explodedBomb.png"
        if index:
            Clock.schedule_once(partial(self.explode_bombs, ind-1), 0.3)
        else:
            print("reached else")
            for bomb in self.bombs.children[:]:
                self.bombs.remove_widget(bomb)
                del bomb
            self.pause_button.text = "Resume"
            self.paused = True
            if self.lives == 2:
                self.bucket.source = "img/2buckets.png"
                self.bucket.size = [75, 75]
            elif self.lives == 1:
                self.bucket.source = "img/1bucket.png"
                self.bucket.size = [75, 25]
            elif self.lives == 0:
                print("LOOOOOSSSSSERRRRRRRR")
                self.__del__()
                print(self.children)
                self.__init__()
                print(self.children)

            self.exploding = False

    def __del__(self):
        for widg in self.children:
            self.remove_widget(widg)
            del widg
        self.remove_widget(self.bomber)
        self.remove_widget(self.bombs)


class KaboomApp(App):

    def build(self):
        game = KaboomGame()
        # Clock.schedule_interval(game.drop_bomb, 1)
        # drop = Clock.schedule_interval(game.update, 1.0/60.0)
        # Clock.schedule_interval(partial(self.pause, drop), 7)
        # Clock.schedule_interval(partial(self.resume, game.drop_bomb), 9)
        return game


if __name__ == '__main__':
    KaboomApp().run()
