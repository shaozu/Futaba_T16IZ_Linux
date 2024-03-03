# Futaba T16IZ Linux Driver 

This simple python script enables you to use Futaba T16IZ controller on Linux. If you want to play simulators like TRYP or RealFlight on Linux, this package is for you.

This repo is inspired by [dji-mini-controller-linux-driver](https://github.com/catrielmuller/dji-mini-controller-linux-driver).

Note: This package is tested on Ubuntu 20.04 and 22.04.

## How to use
Because usb operations require root privileges, you need to run the script under `root`. Open a terminal and type the following commands.

```
git clone https://github.com/shaozu/Futaba_T16IZ_Linux
cd Futaba_T16IZ_Linux
sudo su    # switch to root
pip3 install -r requirements.txt
python3 entry.py
```
If everything works well, you can open your simulator and enjoy your flying.

Normally most simulators support channel reverse, but if not, you can manually reverse the channel i by toggling the i-th component of list `event_reverse_flag` in `entry.py`. 

## Adapt to other Futaba Controllers
If you want to use this script with other Futaba controllers, you need to find out the product id of your specific controller using `lsusb -v`. Modify the `FUTABA_T16IZ_PRODUCT_ID` variable in `entry.py` and you're ready to go.