# OFXfix

This is a small code snippet/script to clean up OFX data downloaded from your bank in order to load it into financial software in a cleaner way.

Requires python >= 3.6.

# Installation

 1. Install `pipenv` using `pip`:

    `pip3 install pipenv`

 2. Configure pipenv for mac with Python2/3 both installed

    `pipenv --python /usr/bin/python3`

 3. Clone this repository:

    `git clone https://github.com/tedcarnahan/ofxfix`

 4. Run `pipenv` to install dependencies:

    ```
    pipenv install
    ```

 5. Run the script within a `pipenv shell`

    ```
    pipenv shell
    (ofxfix) % python3 ofxfix.py
    ```
# Logging

Use flag `-v DEBUG` to see debug logging.