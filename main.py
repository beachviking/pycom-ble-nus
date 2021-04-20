
"""
Created on Mon Apr 12 15:40:07 2021
@author: Gunnar Larsen
@license: MIT-license

This file contains a bare bone implementation of the BLE Nordic Uart Service(NUS) on a
Pycom device.

As an example, a simple guessing game where the BLE app user must try to guess a 
number between 0 and 255 is implemented.

Use the Bluefruit Connect app to play.  Select the UART profile and under settings,
make sure local echo and send Eol options are enabled.

Have fun.

"""

from bleuart import BLEUart
from time import sleep
from uos import urandom

class GuessingGame:
    def __init__(self):
        self.new_game()

    def new_game(self):
        self.secret_number = int(os.urandom(1)[0])
        self.num_guesses = 0

    def evaluate(self, command):
        msg = 'Huh?'

        if (command.isalpha()):   
            if (command == 'hello'):
                msg = 'Hello to you too!'

            if (command == 'new'):
                self.new_game()
                msg = 'Guess my number!'

        if (command.isdigit()):
            guess = int(command)

            if (guess > self.secret_number):
                msg = 'My number is lower'
                self.num_guesses += 1

            if (guess < self.secret_number):
                msg = 'My number is higher'
                self.num_guesses += 1

            if (guess == self.secret_number):
                msg = 'You guessed my number in ' + str(self.num_guesses) + ' tries!'

        return msg

bleuart = BLEUart()
game = GuessingGame()

bleuart.begin('NUS Game')

while(True):
    if (bleuart.available_data()):
        new_data = bleuart.get_data()
        response = game.evaluate(new_data.rstrip())
        bleuart.write(response)

    sleep(1.0)
