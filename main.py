"""Flappy Bird game."""
from tkinter import *
import random


class GUI:
    """Controls all actions within the game."""

    # width and height of the GUI canvas
    _WIDTH = 800
    _HEIGHT = 600
    # time delay for window.after (in milliseconds)
    _GAME_SPEED = 15
    # the button that will control the game function (ie Bird flap)
    _GAME_BUTTON = "space"
    _BACKGROUND_COLOUR = "black"

    def __init__(self):
        """Initialise the GUI class."""
        self._window = Tk()
        self._canvas = Canvas(self._window, width=self._WIDTH,
                              height=self._HEIGHT,
                              background=self._BACKGROUND_COLOUR)
        self._bird = Bird(self._canvas, self._WIDTH / 4 -
                          (Bird.WIDTH / 2), self._HEIGHT / 2 -
                          (Bird.HEIGHT / 2))
        # list that holds the top and bottom pipes
        self._pipe_list = []
        # set the pipe to the edge of the GUI window
        self._pipe_position = self._WIDTH
        # gets when users presses a key
        self._canvas.bind_all("<{}>".format(self._GAME_BUTTON),
                              self._key_press)
        # gets when users key release
        self._canvas.bind_all("<KeyRelease>", self._key_release)
        self._game_score = 0
        # stores key input values
        self._keys_pressed = []
        self._game_running = False

        # Initialize the labels
        self._instructions_label = None
        self._start_label = None
        self._score_label = None
        self._create_labels()

        # Boolean that flip when the key is pressed
        self.is_key_pressed = False
        # variable instance of the .after identifier
        self._after_function_identifier = None

        # makes the Tkinter window non-scalable
        self._window.resizable(False, False)
        self._canvas.pack()
        self._window.mainloop()

    def _update(self, updated_function):
        """Call the .after function."""
        # this sets the .after function identifier
        # this will allow me to cancel the .after function when the game ends
        self._after_function_identifier = self._window.after(self._GAME_SPEED,
                                                             updated_function)

    def _create_labels(self):
        """Create instructions label."""
        self._start_label = Label(self._canvas,
                                  text="Press SPACE to start the game",
                                  fg="white", bg="black")
        # puts the start label in the center of the GUI canvas
        # relx and rely are fractions (50% of the width and 50% of height)
        self._start_label.place(relx=0.5, rely=0.5, anchor="center")

        self._instructions_label = Label(self._canvas,
                                         text="HOW TO PLAY: "
                                              "Press SPACE to Jump",
                                         fg="white", bg="black")
        # puts the instructions just below the start label
        # relx - middle on the x-axis. rely 60% from the top of canvas
        self._instructions_label.place(relx=0.5, rely=0.6, anchor="center")

        self._score_label = Label(self._canvas, text=f"{self._game_score}",
                                  fg="lime green", bg="black")
        # puts the score label at the top of the canvas in GUI
        # relx - middle on the x-axis. rely 20% from the top of canvas
        self._score_label.place(relx=0.5, rely=0.2, anchor="center")

    def _reset(self):
        """Reset the game."""
        # gets rid of everything in the canvas
        self._canvas.delete("all")
        self._game_running = False
        # cancels the .after function
        self._window.after_cancel(self._after_function_identifier)
        # clears the pipe list
        self._pipe_list.clear()
        # gets rid of the score label to make way for a new one
        self._score_label.destroy()
        # reset the score label
        self._game_score = 0
        # moves the bird back to the start position
        self._bird.move_to_initial_position()
        self._bird = Bird(self._canvas, self._WIDTH / 4 -
                          (Bird.WIDTH / 2), self._HEIGHT / 2 -
                          (Bird.HEIGHT / 2))
        # put the start and instruction labels on the canvas
        self._create_labels()

    def _check_collision(self):
        """Detect when bird hits the pipes."""
        bird_position = self._canvas.coords(self._bird.bird_id)
        # find if the bird overlaps with anything in the canvas
        collision = self._canvas.find_overlapping(*bird_position)
        # if the bird collides with somthing or goes outside GUI
        if (len(collision) > 1 or bird_position[3] > self._HEIGHT
                or bird_position[1] < 0):
            self._reset()

        # Check if the bird has passed any pipes
        for pipe in self._pipe_list:
            # if the bird passes the pipe and has not been passed before
            if (bird_position[2] >= self._canvas.coords(pipe.top_pipe_id)[0]
                    and not pipe.passed):
                # tell the pipes that they have been passed
                pipe.passed = True
                self._game_score += 1
                # update the same score label
                self._score_label.config(text=f"{self._game_score}")

    def _create_pipe(self):
        """Create a set of pipes."""
        if (len(self._pipe_list) == 0
                or self._pipe_position <= (self._WIDTH - Pipe.PAIR_SPACING)):
            # creates a random number in between the pipes MAX & MIN Heights
            gap_y_position = random.randint(Pipe.MIN_HEIGHT, Pipe.MAX_HEIGHT)
            # create top and bottom pipes
            pipe = Pipe(self._canvas, self._WIDTH, gap_y_position - Pipe.GAP)
            # puts top and bottom pipes in their respected lists
            self._pipe_list.append(pipe)
            # rest pipe position to edge of GUI window
            self._pipe_position = self._WIDTH
            # when the pipe reaches the left hand side of the canvas
            if self._pipe_position == 0:
                # remove pipes
                self._pipe_list.remove(pipe)
                pipe.delete()
        else:
            # keep the pipes moving across the canvas to the left
            self._pipe_position -= 1

    def _key_press(self, event):
        """
        When key is pressed, check if the key pressed is the _GAME_BUTTON.

        if yes, then make the bird flap and if the game has not started uet,
        start game.
        if no, do nothing
        """
        if event.keysym == self._GAME_BUTTON and not self.is_key_pressed:
            self.is_key_pressed = True
            if not self._game_running:
                self._start_game()
                # give the bird an initial flap upon the game starting
                self._bird.flap()
                self._score_label.config(text=f"{self._game_score}")
            else:
                self._bird.flap()

    def _key_release(self, event):
        """
        When key released, remove key press from set.

        and set is_key_pressed to false
        """
        if event.keysym == self._GAME_BUTTON:
            self.is_key_pressed = False

    def _start_game(self):
        """
        Start the game.

        get rid of instruction and start label
        and tell the Bird and Pipe to move
        """
        self._game_running = True
        # get rid of the start and instruction labels
        self._instructions_label.destroy()
        self._start_label.destroy()
        # start to move the bird and the pipes
        self._move_bird()
        self._move_pipe()

    def _move_bird(self):
        """
        Tell bird class to move the bird.

        is GAME_BUTTON is pressed, flap Bird
        if the game is running, update game
        """
        self._bird.move()
        if self._GAME_BUTTON in self._keys_pressed:
            self._bird.flap()
        self._check_collision()
        if self._game_running:
            self._update(self._move_bird)
        else:
            self._game_running = False

    def _move_pipe(self):
        """Tell the pipe class to move the pipe."""
        for pipe in self._pipe_list:
            pipe.move()
        self._create_pipe()
        if self._game_running:
            self._update(self._move_pipe)


class Bird:
    """Bird object for game."""

    # Height and width of the Bird
    WIDTH = 15
    HEIGHT = 15
    _COLOUR = "White"

    def __init__(self, canvas, x_pos, y_pos):
        """
        Initialise the Bird class.

        canvas: reference to the canvas object created in the GUI
        x_pos: the x-position of the Bird the canvas
        y_pos: the y-position of the Bird on the canvas
        """
        self._canvas = canvas
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._y_vel = 3
        self._y_flap = 15
        self.bird_id = self._canvas.create_rectangle(self._x_pos, self._y_pos,
                                                     self._x_pos + self.WIDTH,
                                                     self._y_pos + self.HEIGHT,
                                                     fill=self._COLOUR)

    def move(self):
        """Move the bird down as if there is gravity."""
        # x_vel is zero
        self._canvas.move(self.bird_id, 0, self._y_vel)
        self._y_vel += 1

    def flap(self):
        """Flap the bird upwards."""
        self._y_vel = -self._y_flap

    def move_to_initial_position(self):
        """Move the bird to its initial position."""
        self._canvas.coords(self.bird_id, self._x_pos, self._y_pos,
                            self._x_pos + self.WIDTH,
                            self._y_pos + self.HEIGHT)


class Pipe:
    """Pipe object for the game."""

    MAX_HEIGHT = 550
    MIN_HEIGHT = 200
    _WIDTH = 50
    # gap between the pair pipes
    GAP = 75
    # distance between each pair of pipes
    PAIR_SPACING = 50
    _COLOUR = "White"

    def __init__(self, canvas, x_pos, y_pos):
        """
        Initialise the Pipe class.

        canvas: reference to the canvas object created in the GUI
        x_pos: the x-position of the Pipe the canvas
        y_pos: the y-position of the Pipe on the canvas
        """
        self._x_vel = -10
        self._canvas = canvas
        self._x_pos = x_pos
        self._y_pos = y_pos
        self.passed = False

        # bottom pipe
        self.bottom_pipe_id = self._canvas.create_rectangle(self._x_pos,
                                                            self._y_pos
                                                            + self.GAP,
                                                            self._x_pos
                                                            + self._WIDTH,
                                                            self._y_pos
                                                            + self.MAX_HEIGHT
                                                            + self.GAP,
                                                            fill=self._COLOUR)

        # top pipe
        self.top_pipe_id = self._canvas.create_rectangle(self._x_pos,
                                                         self._y_pos
                                                         - self.GAP,
                                                         self._x_pos
                                                         + self._WIDTH,
                                                         self._y_pos
                                                         - self.MAX_HEIGHT
                                                         + self.GAP,
                                                         fill=self._COLOUR)

    def move(self):
        """Move the top and bottom pipes."""
        # y_vel is zero
        self._canvas.move(self.bottom_pipe_id, self._x_vel, 0)
        self._canvas.move(self.top_pipe_id, self._x_vel, 0)

    def delete(self):
        """Delete instance of class."""
        # deletes both pipes from the canvas
        self._canvas.delete(self.top_pipe_id)
        self._canvas.delete(self.bottom_pipe_id)
        # deletes instance of class
        del self


if __name__ == "__main__":
    GUI()