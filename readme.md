
# Prerequisites

You need python v3 installed, pip and venv.

# How to run

1. You need the QR code in png format.  The script expects it to be in the working directory and named `in.png`
2. Execute this to get the venv with its libraries ready:

```
python3 -m venv venv
. venv/bin/activate
pip install python-jose
pip install Pillow
pip install pyzbar
```

3. Execute this to run the script:

```
./decode.py
```

