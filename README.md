# pyhide
Use steganography to hide data in images. 

The Least Significant Bit method is used when a base image is provided, where the data will be written to the end of each pixel. More bits will be used depending on how much data is to be stored, and not providing a base image will force it to use all 8 bits.

These images must be saved as a lossless format (such as .PNG), and any resampling will lose the data. Some image hosts such as Imgur will not reformat the image if it's below a certain size, making it an ideal host to use for sharing.

## Installation
```
pip install pyhide
```

## Example Usage
```python
# Simple image encode/decode
>>> encoded_image = PyHide(data).image_encode()
>>> data == PyHide.image_decode(encoded_image)
True

# Encode using a base image, forcing RGB
>>> image = image_from_url(url)
>>> encoded_image = PyHide(data).image_encode(mode='RGB', base=image)
>>> data == PyHide.image_decode(encoded_image)
True
```

The returned images are instances of `PIL.Image`, which contains the save functionality if needed. `pyhide` by itself does everything in memory and will not write anything to disk.
