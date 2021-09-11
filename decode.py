#!/usr/bin/env python3

import base64
import zlib
import sys
from jose import jwk
from jose.utils import base64url_decode
from PIL import Image
from pyzbar.pyzbar import decode

from textwrap import wrap


def pad_base64(data):
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '='* (4 - missing_padding)
    return data


barcodes = decode(Image.open("in.png"))

if (len(barcodes) == 0):
  print("Failed to open in.png")
  exit(1)

qr_text=barcodes[0].data.decode("UTF-8")

print( "QR Code raw content:\n\n " + qr_text + "\n\n")

qr_parts=qr_text.split('/')
if (qr_parts[0] != 'shc:'):
  print("That is not a shc QR code.")
  exit(1)

qr_text = qr_parts[1]

# Split in chunks of 2 characters each to get a sequence of 2 digits numbers
chars = wrap(qr_text, 2)

# Decode this numeric encoded string (Add 45 to each to get the ascii code)
decoded_str = ""
for current_char in chars:
  decoded_str += chr(int(current_char)+45)

# At this point we have a JWT token
print ("Here's the compressed JWT token decoded from the numeric string:\n\n " + decoded_str +"\n\n")

b64_header, b64_jwt, b64_signature = decoded_str.split('.')

header = base64.urlsafe_b64decode(pad_base64(b64_header)).decode('utf-8')

print ("Here's the JWT Header:\n " + header +"\n\n")

# The jwt payload of a shc token is always deflated using headerless zlib compression so we must inflate that here
jwt_payload = zlib.decompress(base64.urlsafe_b64decode(pad_base64(b64_jwt)), -15).decode('utf-8')

# Reconstitute the JWT Token after recoding the decompressed payload back in base64
jwt_token = b64_header + "." + pad_base64(base64.b64encode(jwt_payload.encode('utf-8'))).decode('utf-8') + "." + b64_signature

print ("The decompressed JWT Token:\n " + jwt_token +"\n\n")

# We now have the inflated JSON payload of the JWT token, display it
print ("The JWT Payload:\n " + jwt_payload +"\n\n")

print ("JWT Signature: " + b64_signature +"\n")

# Let's hardcode the public key...
pubkey = {
    "kid": "sAEPPhsLoTv5g5HoPQjumbbEm4F1ZD6D2JhuOyl_mLc",
    "alg": "ES256",
    "kty": "EC",
    "crv": "P-256",
    "use": "sig",
    "x": "XSxuwW_VI_s6lAw6LAlL8N7REGzQd_zXeIVDHP_j_Do",
    "y": "88-aI4WAEl4YmUpew40a9vq_w5OcFvsuaKMxJRLRLL0",
}

print ("Now verifying signature...")
# Verify the signature

jwkkey = jwk.construct(pubkey)
decoded_sig = base64url_decode(pad_base64(b64_signature))
decoded_body = base64url_decode(pad_base64(b64_jwt))
res = jwkkey.verify((b64_header+"."+b64_jwt).encode(), decoded_sig)
print("res:" + str(res))
if res:
  print("This QR code is valid!")
  # At this point we know we trust the info stored in the token.
  # We could validate that the vaccines are approved, two doses at least were received, etc
  # We can also retrieve the patient's name and print it.
else:
  print("This QR code is invalid!  Or at least, it was not signed by sante-quebec.")


