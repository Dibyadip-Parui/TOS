

all: build/boot.bin build/load.bin

build/boot.bin: src/boot/boot.asm build
	nasm -f bin $< -o $@

build/load.bin: src/boot/loader.asm src/boot/BootLib/text.asm src/boot/BootLib/memory.asm
	nasm -f bin $< -o $@

build:
	mkdir build

clean:
	rm -rf build/
run:
	qemu-system-x86_64 -hda disk/disk.img