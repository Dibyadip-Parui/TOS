[org 0x7c00]

jmp 0x0000:BootStart

BootStart:
    mov [DRIVE_NO], dl
    setup:
        xor eax, eax
        mov ebx, eax
        mov ecx, eax
        mov edx, eax
        mov edi, eax
        mov esi, eax

        mov ds, ax
        mov es, ax
        mov fs, ax
        mov gs, ax

        mov ax, 0x1000
        mov ss, ax
        xor ax, ax
        mov sp, 0xFFFF
        mov bp, sp
    
    printing:
        mov ah, 0x0e
        mov al, 'B'
        int 10h
        mov al, 'O'
        int 10h
        mov al, 'O'
        int 10h
        mov al, 'T'
        int 10h
        mov al, 'E'
        int 10h
        mov al, 'D'
        int 10h

    pass1:
        ;loading stage2 loader from BootFS
        mov ah, 0x02
        mov al, 4
        mov ch, 0
        mov cl, 2
        mov dh, 0
        mov dl, [DRIVE_NO]
        mov bx, 0x7e00

        int 13h
        jc .error
        jmp 0x7e00
    
.halt:
    hlt
    jmp .halt
.error:
    mov ah, 0x0e
    mov al, ' '
    int 10h
    mov al, 'E'
    int 10h
    jmp .halt
DRIVE_NO: db 0

times 446-($-$$) db 0

MBR:
    part1:
        db 0x80
        db 0, 0, 0
        db 0x4F ;TOS bootloader partition
        db 0, 0, 0
        dd 0x00000001 ;Starting address
        dd 0x00000004 ;total number of sectors
    part2:
        dq 0, 0
    part3:
        dq 0, 0
    part4:
        dq 0, 0

dw 0xaa55

start:
    call NL
    lea di, [msg]
    call print

    

.halt2:
    hlt
    jmp .halt2

NL:
    pusha

    mov ah, 0x03
    mov bh, 0x0000
    int 10h

    mov ah, 0x02
    mov bh, 0x00
    inc dh
    mov dl, 0
    int 10h

    popa
    ret
print:
    pusha
    
    mov ah, 0x0e
    .loop:
        mov al, [di]
        
        cmp al, 0
        je .exit

        int 10h
        inc di
        jmp .loop
    
    .exit:
        popa
        ret
DAP:
    .SIZE: db 0x10 ;size of this DAP
    .RESERVED: db 0x00 ;reserved should be 0
    .S2R: dw 0x0000 ;Sectors to load
    .DLA: dw 0x0000 ;Destination load address
    .DLS: dw 0x0000 ; Destination load segment
    .LBA: dq 0x0000000000000000 ;Disk sector to load

msg: db "Loaded Stage2 Loader.", 0
times (2048+512) - ($-$$) db 0