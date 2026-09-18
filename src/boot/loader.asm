[org 0x0000]
bits 16

CODE_SEG equ gdt_code - gdt_start
DATA_SEG equ gdt_data - gdt_start

start:
    .setup:
        ;just a bit of cleaning up.....
        xor eax, eax
        mov ebx, eax
        mov ecx, eax
        mov edx, eax
        mov edi, eax
        mov esi, eax

        mov es, ax
        mov fs, ax
        mov gs, ax

        mov ax, 0x2000
        mov ss, ax
        mov sp, 0xffff
        mov bp, sp

        mov ax, 0x1000
        mov ds, ax
        xor ax, ax
    
    ;finaly we have space

    lea di, msg
    call print
    add sp, 2

halt:
    hlt
    jmp halt

GDT:
    gdt_start:
        dq 0
    gdt_code:
        dw 0xFFFF                   ; Limit (bits 0-15)
        dw 0x0000                   ; Base (bits 0-15)
        db 0x00                     ; Base (bits 16-23)
        db 10011010b                ; Access byte: Present, Ring 0, Code, Executable, Readable
        db 11001111b                ; Flags (4 bits) + Limit (bits 16-19): Granularity (4KB), 32-bit
        db 0x00                     ; Base (bits 24-31)

    gdt_data:
        dw 0xFFFF                   ; Limit (bits 0-15)
        dw 0x0000                   ; Base (bits 0-15)
        db 0x00                     ; Base (bits 16-23)
        db 10010010b                ; Access byte: Present, Ring 0, Data, Writable
        db 11001111b                ; Flags (4 bits) + Limit (bits 16-19)
        db 0x00                     ; Base (bits 24-31)

    gdt_end:
gdt_descriptor:
    dw gdt_end - gdt_start - 1  ; Size of GDT (limit)
    dd gdt_start                ; Base address of GDT

msg: db "Stage 2 Bootloader loaded.", 0
;including the files
%include "src/boot/BootLib/text.asm"