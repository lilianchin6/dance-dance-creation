# dance dance creation

This repository contains computer version of the game Dance Dance Revolution, similar to StepMania, where players use arrows on the computer to match beats with the music. Instead of using pre-selected songs, this program allows players to import their own songs in `.wav` format, where this program will analyze the music and provide an arrow sequence to the beats of the song. There is single-player, multi-player, and a no-fail mode. This is written in Python 2.

This game was written as a final project to a class Spring 2015 using the professor's `eventBasedAnimation.py` file.


# How to Run

#### 1) Create and start a virtual environment

- `pip install virtualenv`
- `python3 -m venv env`

##### On Mac:
- `source env/bin/activate`

##### On Windows:
- `env\Scripts\activate`

#### Install requires packages

- `pip install -r requirements.txt`

In command line, run `python dance.py`


############################################################################################################


Modules used: aubio, pygame, tkinter, eventBasedAnimation


```
At the top of the code, should be able to successfully import:
import sys, os
import eventBasedAnimation
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import tkMessageBox

from aubio import source, onset

from pygame.locals import *
from pygame.mixer import music
import pygame as pg
import string
import random
```
