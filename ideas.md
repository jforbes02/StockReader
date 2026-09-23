# StockReader


## Day 0 
Inspired by a cool cv project I saw on LinkedIn that showcased Pokémon card prices using snapchats vr glasses
https://lnkd.in/p/eB9JYy4t

Basically I want to have the same concept but with these reqs(for lack of better words)
Today is just planing

- Whenever the camera picks up a logo of a company the 
  - price of the stock shows
  - ticker symbol of the stock shows
  - history graph of the stock shows
  - maybe a prediction graph of the stock??

In the future maybe implement a way to add this into the apple vision pros?

I'm trying to limit my use of AI in this project so this file will hold a lot of links and sources

I've made a CV project before for my capstone → https://github.com/jforbes02/Align

In that project I utilized Mediapipe Kotlin and Fastapi
In this project I want to focus on the speed and accuracy of the proj rather than completeness which was the prior proj

My idea for tech stack from now (0 planning so far) is:
- Swift Frontend
  - I want to learn SwiftUI
  - I know that Swift has its own vision framework
- Python Backend
  - Pytorch ML training in order to identify logos

Will be splitting this proj up into Daily inputs ~ As I am a college student and work two jobs everyday may not have an 
input!

## Day 1 - Learning PyTorch + Finding Datasets

Today I want to get familiar with PyTorch as im pretty sure that will be the meat and bones of this project

I know that this is a image recognition proj so Deep Learning is necessary.

# Transfer Learning
After doing some research came across the concept of Transfer Learning

Currently watching this video https://www.youtube.com/watch?v=K0lWSB2QoIQ

- Transfer Learning is a method where a model made for a task is used for another task with slight modifications
- Typically change the last layer of model
- Good for rapid generation of models

reading through this https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

I don't think ImageNet will be a dataset that would be good for this project.
Currently searching for logo datasets

I think starting with S&P datasets would make the most sense~
Found this dataset I think I will use https://github.com/msn199959/Logo-2k-plus-Dataset

This API could be what I use to get the clean logos that will show up on the scans https://brandfetch.com/developers

### Dataset - Logo-2k-plus
Will be using logos from the S&P 100
First will parse them into a folder /logos

Used Claude Code to get list of S&P folders 


    'SP100_FOLDERS = [
    # Electronic
    'AMD',
    'Apple',
    'Cisco Systems',
    'Honeywell',
    'IBM',
    'Intel',
    'Microsoft',
    'Texas Instruments',  # found under Medical/

    # Transportation
    'Tesla',

    # Accessories
    'Nike',

    # Food
    'coca cola',
    'Costco Wholesale',
    'McDonald\'s',
    'pepsi',
    'Starbucks',

    # Institution
    'Amazon at Lab126',
    'Chevron',
    'Exxon',
    'General Electric',
    'Google',
    'J.P. Morgan',
    'John Deere',
    'Marathon Petroleum',
    'Marriott International',
    'Target',
    'Walmart',

    # Cosmetic
    'Johnson & Johnson',

    # Medical
    'Colgate',

    # Leisure
    'Disney']

Looking at Amazon at Lab126 it looks outdated, might want to use better data?

Even google is old the Dataset seems extremely old, Maybe swap to LogoDet-3k?

I see that in LogoDet-3k it is a bit different in that it labels items
