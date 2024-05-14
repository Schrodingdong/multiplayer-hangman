# Hangman in terminal
A simple Hang man implementation in ~~Rust~~ Python

## How run it ?
### directly
```bash
./hangman.ps1
./hangman.bat
./hangman.sh
```

Make sure to set $NGROK_TOKEN if using linux
### Manually
- make sure to have ngrok, python & pip installed
- install dependencies in requirements.txt
```bash
pip install -r ./requirements.txt
```
- run the main script
```bash
python ./python_impl/src/main.py
```
- if you are hosting : start ngrok (DONT FORGET TO `ngrok config ....` FOR CONNECTION TOKEN)
```bash
ngrok http 8000 
```


## Dependencies
### Ngrok 
install ngrok from here : [ngrok.com](https://ngrok.com)
### Python modules
modules to be installed :
- websockets
- requests
