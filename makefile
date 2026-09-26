

all: boot.bin run
build: boot.bin

boot.bin: src/boot/boot.asm BuildDir
	nasm -f bin src/boot/boot.asm -o build/boot.bin

BuildDir: clean
	mkdir build

run:
	qemu-system-x86_64 build/boot.bin

clean:
	rm -rf build