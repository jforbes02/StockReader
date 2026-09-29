# StockReader


# Day 0 
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
  - FastAPI api that gets stock information

Will be splitting this proj up into Daily inputs ~ As I am a college student and work two jobs everyday may not have an 
input each day!

# Day 1 - Learning PyTorch + Finding Datasets

Today I want to get familiar with PyTorch as im pretty sure that will be the meat and bones of this project

I know that this is a image recognition proj so Deep Learning is necessary.

## Transfer Learning
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

# Day 2 - Dataset Parsing
Today I want to complete parsing the dataset into a logos folder

I find interesting about these datasets is that there aren't much of the biggest companies

Therefore, I am thinking about creating my own dataset with the MAGS companies (to lower load on myself)
Currently only thing that LogoDet-3k has is Apple, while logo2k+ has apple old amazon nvidia and tesla

I think i may try to get Claude to automate this task as it seems tedious

# Day 3 - Dataset Work continued

Past few days I was very sick, so I have not worked on this but I am back, 
the goals for today are
- Complete a quality dataset
- Start training

I have managed to get pictures of the mag7 brands and I went through and took out any outliers that shouldn't be there

One thing that I am curious about is the watermark issue, how much will the watermarks on some data affect the model?

Currently reading documentation as videos only show the bees/ants examples
https://docs.pytorch.org/vision/stable/auto_examples/transforms/plot_transforms_getting_started.html#sphx-glr-auto-examples-transforms-plot-transforms-getting-started-py

Learning what exactly a Tensor is
https://www.youtube.com/watch?v=L35fFDpwIM4
https://www.youtube.com/watch?v=kgOXgoceJGQ
https://www.youtube.com/watch?v=lOGd6ysc2j4

Tensors are a data structure that are specialized for gpu accelerated work
Good for large data

Using this vid for guidance 
https://www.youtube.com/watch?v=CtzfbUwrYGI

When transfer learning ImageNet normalization should be 
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])

Digging deeper into ResNet
https://www.youtube.com/watch?v=o_3mboe1jYI

Digging into CNNs
https://www.youtube.com/watch?v=QzY57FaENXg

Thinking that maybe I should've used a jupyter notebook, but we digress

Created a function that gathers the Training and Validation datasets along with classes that are determined by the folder names

Moving onto training reading this documentation
https://docs.pytorch.org/docs/2.14/generated/torch.optim.lr_scheduler.LRScheduler.html

Created a model building function that builds the transfer training model prior to training
 

    model = models.resnet18(weights='DEFAULT')
    model.fc = nn.Linear(model.fc.in_features, len(x)) #creates final layer with 512 inputs that give 7 class scores
    model.to(dev) #sends model to GPU or CPU

This gets the resnet set and creates a final layer that has 512 inputs into however much classes needed for output from my model

Out of curiosity read the first page of this paper on the resnet page
https://arxiv.org/pdf/1512.03385

When implementing training got interested in .train() from torch.nn.modules.module
https://stackoverflow.com/questions/51433378/what-does-model-train-do-in-pytorch
https://docs.pytorch.org/docs/2.14/generated/torch.nn.Module.html

Completed the first training results below

    train Loss: 0.0902  Acc: 0.9932
    val Loss: 0.2818  Acc: 0.9293
    Training complete in 13m 28s
    Best val Acc: 0.9348

Tomorrow I will work on adding a simple api endpoint that gets stock information and sstart to learn Swift and its 
capabilities.

# Day 4 - My Stock Endpoint

I want to take a little break from the ML model and start focusing on creating the endpoint that I will need for getting
1. Stock Ticker Symbol
2. Stock Histograph
3. Stock img
4. Maybe stock prediction

It shouldn't be too hard
I assume I will just need an api key and a single Get endpoint

## Finding An API
Earlier I found Brandfetch that has nice logos of the companies I want in this format

<img src="https://cdn.brandfetch.io/ticker/TSLA?my_api_key" alt="Logo by Brandfetch" />

Some things im not sure about are
1. Will this work in a 3D VR sense?
2. Can this html be utilized in Swift?

Will be using yfinance as the service to get a graph of data

I plan on getting the data into json format then on the Swift frontend creating a graph using this data
(I want a 3D graph will see if that is possible in the future)

Reading through the documentation -> http://ranaroussi.github.io/yfinance/

Not sure if there's a problem but the Documentation is pretty bad lol

https://www.alphavantage.co/documentation/
Alpha Vantage has a free api that looks promising

Provides for me data for open, high, low, closing, and volume for each day in the past week
Exactly what I wanted for the data
Even returns the data in a JSON which is perfect for SwiftUI 

reading https://github.com/pydantic/httpx2

So I was able to create an endpoint that gives information on stocks prices when the market closes and opens along with 
their low and high for the day using alphavantage API 

I think that the next step will be learning SwiftUI and figuring out how the endpoint will work with VR features
Also have been having thoughts of having it be compatible with the apple vision pros but im not entirely sure yet if I 
even have access to develop things for that hardware

Some of my code from today below


    data = httpx2.get("https://www.alphavantage.co/query",
                        params={'function': 'TIME_SERIES_DAILY',
                                'symbol': mag7_symbols[company.upper()],
                                'apikey': stock_history_key,
                                'datatype': 'json',
                        },
      )
  
      #for errors
      data.raise_for_status()
      x = data.json()
      time = x.get("Time Series (Daily)")
      if not time:
          raise HTTPException(status_code=502, detail="No data found - issue with API provider")
  
      dates = sorted(time.keys(), reverse=True)[:7]
      return [{"date": d, "open": float(time[d]["1. open"]),"high": float(time[d]["2. high"]),"low": float(time[d]["3. low"]), "close": float(time[d]["4. close"])} for d in dates]

Tommorow I will work on learning Swift

