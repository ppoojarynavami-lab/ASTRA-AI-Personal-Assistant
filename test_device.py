

from modules.device_control import change_volume, change_brightness

print("\nTesting volume...")
print(change_volume("increase", 10))

print("\nTesting brightness...")
print(change_brightness("increase", 10))

print("\nDevice test completed.")
