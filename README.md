# Python_GPUinfo_Module
**Python module to get the names, and manufacturers, of all connected graphics cards, both dedicated and integrated**

## Installation
Download the [source code](https://github.com/gindvd/Python-GPUinfo/archive/refs/heads/main.zip), paste the `GPUinfo` folder into your project directory

## Example
```python
from GPUinfo import *

connected_gpu_manufacturers = manufacturers()

for idx, name in enumerate(connected_gpu_manufacturers):
  print(f"Connected GPU {idx + 1} manufacturered by {name}")

connected_gpu_names = fullnames()

for idx, name in enumerate(connected_gpu_names):
  print(f"GPU {idx + 1}: {name}")
```

## Methods
- **fullnames()**
    
    Returns a list of all connected GPU names:
    ```python
    connected_gpu_names = fullnames()
    ```

    Output example: ['Intel Corporation UHD Graphics 620', 'NVIDIA Geforce 4070 RTX']

- **manufacturers()**
    
    Returns list of manufacturers of all connected GPUs
    ```python
    connected_gpu_manufacturers = manufacturers()
    ```

    Possible returns options:
    - nvidia - for NVIDIA GPUS
    - amd - for AMD for dedicated and integrated GPUs
    - intel - for Intel for dedicated and integrated GPUs
    - apple - for Apple M-Series integrated graphics
    - adapter - possible return on Virtual Machines and Container hosted OS

### More Details
For an example of uses for this module, visit [GUI_Video_Compressor/_codec_value](https://github.com/gindvd/GUI_Video_Compressor/blob/main/src/app.py#L419)