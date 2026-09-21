# Hardware and power

## Reference stack

The reference build places the 3.5-inch display above the Pi GPIO header and the UPS HAT (D) below the Pi using its pogo-pin connector.

![Assembled unit](../assets/photos/deck-angle.jpg)

The photographed display is labelled `3.5inch RPi Display`, `480x320 Pixel` and `XPT2046 Touch Controller`. The reference configuration uses the `piscreen` overlay and an ILI9486 framebuffer at `/dev/fb0`. It needs no desktop environment.

The UPS normally exposes an INA219 at `0x43` and its microcontroller at `0x2d`. Verify with `sudo i2cdetect -y 1`.

## Correct power path

Connect the charger to the **UPS HAT charging port**, not the Raspberry Pi power port. Powering the Pi separately can bypass the HAT's measurement and backup path. Test deliberately: boot normally, confirm a charged battery, disconnect external charging briefly, and verify that the Pi remains online.

Use matched, reputable cells of the exact type specified by the HAT manufacturer. Observe polarity and fire-safety precautions. Replace damaged, swollen or aged cells. Do not combine independent supplies on the same 5 V rail unless the hardware documentation explicitly permits it.

## Enclosure and cooling

Keep vents clear, avoid conductive surfaces, and prevent cables from levering connectors. Many inexpensive SPI displays have a hard-wired backlight. If its sysfs `max_brightness` is `0`, software backlight control is unavailable without a hardware modification.
