# dirwatcher.py
### Written by David Richardson
#### A Kenzie Academy assignment

Dirwatcher will take in magic text and search a directory looking for files containing that text untill you or the system tell it to stop. Please run only in Python3. The magic text is a positional variable, and the only required information. Other optional variables follow:

1. Directory to search
  * -d or --dir
  * example: "files"
  * default: "./"
2. Polling Interval
  * -i or --int
  * example: 5
  * default: 3
2. File extension
  * -e or --ext
  * example: "log" or ".log"
  * default: "txt"
  
# Example usage
`python3 dirwatcher.py magic` => Search for magic text: `magic`. Default dir: "./", Default polling: 3s, Default extension: "txt"

`python3 dirwatcher.py magic --dir files` => Search `./files` for magic text: `magic`. Default polling: 3s, Default extension: "txt"

`python3 dirwatcher.py magic --dir files --int 5` => Search `./files` for magic text: `magic` every `5`seconds. Default extension: "txt"

`python3 dirwatcher.py magic --dir files --int 5 --ext .log` => Search `./files` for magic text: `magic` in `log` files every `5`seconds.
