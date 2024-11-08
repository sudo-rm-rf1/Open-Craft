# Open Craft
## Description

Completely open source implentation of Neal.fun's [Infinite Craft](https://neal.fun/infinite-craft/). Can run completely locally with no internet.


## What models to use
1. [Mistral 7b OpenOrca](https://huggingface.co/TheBloke/Mistral-7B-OpenOrca-GGUF/tree/main) - Slower but better responses
2. [Phi-3 Mini 128k Instruct](https://huggingface.co/MoMonir/Phi-3-mini-128k-instruct-GGUF/tree/main) - Faster but worse responses
   
## How to play
1. Download a gguf file for one of the models shown above
2. Clone or download the repository
3. Cd into the directory of the repository
4. run `pip install -r requirements.txt`
5. run `python main.py`
6. Enter the path to the gguf file when prompted (Note if you choose to use your own model it may error here. It shouldn't error if you use one of the two shown above)
7. Wait for it to perform checks (Might take a couple minutes depending on the specs of your computer)
8. Open `http://127.0.0.1:5000/`
9. (Note it might run really slow. Currently the model is running on your cpu instead of gpu since I didn't want to deal with driver issues for different cards. Takes around 15-20 seconds on an i7-12700k. Please let me know if yall want an update to make it run on gpu)
   
## Images
![Screenshot 2024-11-08 170106](https://github.com/user-attachments/assets/effad5af-5f94-4e5b-a4f6-84030f63225d)

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
