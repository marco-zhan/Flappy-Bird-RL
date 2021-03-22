# Flappy-Bird-RL

## Introduction

Implementation of Flappy Bird using python and Pygame module. Then, using the reinforcement learning algorithm to train the "brain" to play Flappy Bird

## Dependencies
- Python 3.7 
- Pygame 2.0.0
  
>**Note: You need to install pygame package for this program to run**

>**Install using the command** `pip install pygame==2.0.0`

## What's included
- `Flappy-Bird-RL/brain.py` This file contains the brain class that uses reinforcement learning to  play Flappy Bird
- `Flappy-Bird-RL/flappy.py` This file contains the wrapped version of Flappy Bird game, run this file to train the brain or use the brain to play Flappy Bird
- `Flappy-Bird/flappy.py` This file contains the implementation of Flappy Bird game (unlike the one above, this one is unwrapped, use this one if you only want to play or implement the game)
- `Flappy-Bird/params.py` This file contains the game settings you can change for fun

## How to run 
For Flappy Bird RL
> `python Flappy_Bird-RL/flappy.py [--fps FPS] [--episode EPISODE] [--mode {human, ai, train, train_noui}] [--max MAX]` 

- `--fps FPS` Frame per second of the game, default values
  - Human mode: 30
  - Other mode: 60
- `--episode EPISODE` How many cycles to train, default 1000
- `--mode {human, ai, train, train_noui}` Mode of the game, default "human"
  - human: Normal Flappy Bird game
  - ai: Use AI to play the game
  - train: Train AI to play, with UI
  - train_noui: Train AI to play, without UI
- `--max MAX ` Maximum score per episode, restart the game if agent reach this score, default: 1000

For Flappy Bird
> `python Flappy-Bird flappy.py`

## How to train
Remove `data/qvalue.json`, this file contains the Q values brain ever experienced

1. Set EPISODE = 1K, with train_noui option (this will make training much faster)
> `python Flappy-Bird-RL/flappy.py --mode train_noui`
2. Set MAX SCORE to 10000, EPISODE = 50, with train_noui option to improve a bit more
> `python Flappy-Bird-RL/flappy.py --mode train_noui --eposide 50`
3. Repeat step 2 with lower episode number until reaching the desired score

It takes about two minutes to train the brain from scratch to an expert player (reaching 5000 score in average)
## Background
Thanks to kyokin78 (link to github in Disclaimer) for provoding the basics. Details explanation of Q-Learning reward and State space can be found on his github page

I removed the <b>"last flap penalty"</b> from kyokin78's code and added a <b>"low death penalty"</b>, which gives the Q-Learning a penalty when the bird crashed way much lower than the gap.

## Some improvements
- I encountered <b>"no response"</b> issue when running pygame, this is because pygame has not detected a `pygame.event.*` for a while, pump the game regularly to stop this by calling `pygame.event.pump()`
- Maintaining the Q-values with 5 decimal digits is enough to decide an action. I rounded the Q-value every time to save some calculation
- I added a <b>"low death penalty"</b>, which gives the Q-Learning a penalty when the bird crashed way much lower than the gap.

## Issues
Though, the current implementation is working well, I cannot obtain the result achieved by kyokin78. Once I trained my "brain" for more episodes, it suddenly "forget" everything when reaching 2000+ episodes. It starts to flap all the way to the top of the screen every time. I am thinking this is due to some Q value overflow, or maybe my Q function is incorrect.

<b>Please contact me if anyone know what went wrong, appreciated !!!</b> 

## Maintainer
If you have any enquiries on this project or any other questions, please contact me at `yixiao5898@gmail.com`

## Disclaimer
https://github.com/kyokin78/rl-flappybird