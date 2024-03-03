import usb
import uinput
import time

FUTABA_VENDOR_ID = 0x1008
FUTABA_T16IZ_PRODUCT_ID = 0x000b
FUTABA_FRAME_BYTES = 16

event_max_value = 32768
# 8 channels
event_list = [uinput.ABS_X, uinput.ABS_Y,\
             uinput.ABS_RX, uinput.ABS_RY,\
             uinput.ABS_THROTTLE, uinput.ABS_RUDDER,\
             uinput.ABS_TILT_X, uinput.ABS_TILT_Y]
event_reverse_flag = [False, False, False, False, \
                      False, False, False, False]

def findFutabaEndPoint(device):
    for cfg in device:
        for intf in cfg:
            for endp in intf:
                if usb.util.endpoint_direction(endp.bEndpointAddress) \
                    == usb.util.ENDPOINT_IN and \
                    endp.bmAttributes == 0x3:
                    return endp.bEndpointAddress

def parseDataFrame(data):
    js_data = []
    for i in range(0, len(data), 2):
        ch_read = int.from_bytes(data[i:i+2], byteorder='little')
        # remap data from (min 704, center 2048, max 3392) -> (min 0, center 16384, max 32768)
        ch_read = (ch_read - 704) * 256 // 21
        js_data.append(ch_read)
    js_data.reverse()       # reverse order
    return js_data

def sendVjoy(data):
    for i in range(0, len(event_list)):
        channel_data = event_max_value-data[i] if \
            event_reverse_flag[i] else data[i]
        vjoy.emit(event_list[i], channel_data, syn=False)
    vjoy.syn()      # send out the whole frame


if __name__ == '__main__':

    device = usb.core.find(
        idVendor=FUTABA_VENDOR_ID, idProduct=FUTABA_T16IZ_PRODUCT_ID)

    if device is None:
        print('Futaba T16IZ not found')
        exit(1)
    print('Found Futaba T16IZ controller')    

    events = tuple([evt+(0, 32768, 0, 0) for evt in event_list])
    vjoy = uinput.Device(events, 'Virtual Futaba T16IZ', vendor=FUTABA_VENDOR_ID)
    time.sleep(1)
    print('Virtual device created')

    try:
        # Detach the kernel driver if it's attached
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        device.set_configuration()

        # Find the interrupt IN endpoint
        endpoint = findFutabaEndPoint(device)

        if endpoint is None:
            raise ValueError("Interrupt IN endpoint not found")

        print('Forwarding data... Controller ---> Virtual Device')
        # Continuously read data from the interrupt IN endpoint
        while True:
            try:
                data = device.read(endpoint, FUTABA_FRAME_BYTES, timeout=20)  # Adjust buffer size and timeout as per your device's specifications
                channel_data = parseDataFrame(data)
                sendVjoy(channel_data)
            except usb.core.USBError as e:
                if e.errno == 110:  # Timeout error, continue polling
                    continue
                else:
                    raise  # Reraise the exception for other USB errors

    finally:
        # Release the interface
        usb.util.release_interface(device, 0)
        # Reattach the kernel driver if needed
        device.attach_kernel_driver(0)
        # Reset the device
        device.reset()
        print('Done')

