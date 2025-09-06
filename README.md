# Pi-Homework-Helper
A Raspberry Pi program that helps solve homework problems (specifically real analysis/proof-based mathematics problems) by taking pictures of the problem, solving it through an LLm, and outputting it through audio. The program mainly solves real analysis problems, but a small tweak to the system prompt can adapt it to any other problem (just change a mention of mathematical symbols to how you would ask an LLM to solve the problem normally).

# Requirements

You need a raspberry pi with wireless conmnection likw the Raspberry Pi Zero W, or a flagship model. You also need a camera module attached, and a bluetooth audio device that is connected.

# Setup

1. Clone or download the repository, then create a new venv environment and install the required packages.

2. Replace the OpenAI key string with your own key

3. run the main.py file with `python main.py'

