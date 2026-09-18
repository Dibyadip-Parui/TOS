[org 0x7c00]
bits 16


start:
    .setup:
        ;setting up segment registers
        xor ax, ax
        mov es, ax
        mov ds, ax

        ;saving the disk number
        mov [DiskNo], dl

        ;clearing registers
        mov bx, ax
        mov cx, ax
        mov dx, ax
        mov di, ax
        mov si, ax

        ;setting up the stack at address 0x2ffff
        mov sp, 0x2000
        mov ss, sp
        mov sp, 0xffff
        mov bp, sp

    push bp
    lea si, partition
    mov bp, si
    add bp, 64

    .loop:
        
        mov al, [si+0x4]
        cmp al, 0x5F
        je .done

        add si, 16
        cmp si, bp
        mov al, 1
        je err 
        jmp .loop
    .done:
        pop bp

    .LoadSFS1:
        push si    
        mov eax, [si+0x08]
        mov word [DAP.S2R], 0x01
        mov word [DAP.DEA], 0x7e00
        mov word [DAP.DES], 0x0000
        mov dword [DAP.STAl], eax
        mov dword [DAP.STAh], 0

        mov ah, 0x42
        mov dl, [DiskNo]
        mov si, DAP
        int 0x13
        mov al, 2
        jc err
    ;

    mov cx, 0x7e00
    mov bx, cx
    add bx, 480
    .loop2:
        add cx, 0x20 ;0x20 = 32
        mov si, cx
        mov di, loader
        call CmpStr

        cmp al, 0
        je .loop2e

        cmp cx, bx
        mov al, 3
        ja err
        jmp .loop2

    .loop2e:
    ;after this sucess we got the entry pointer in cx and si
    ;but we willdiscard that saved si in stack
    pop di
    mov edx, [di+0x08]
    push edx
    mov si, cx
    ;now we only have the pointer in si whic is certainly a good thing..... Yea Certainly
    mov di, cx
    add di, 30
    mov ax, [di]
    ;Yaa now we have the pointer to the starting sectors in the LBA for our loader in al
    ;but the pointer are ofset so to get the real lba we need to add te pointer with the partition starting sector
    ;and also numbr of sectors to read in ah
    xor bx, bx
    mov bl, ah
    add ebx, edx
    ;loading the pointer table of the file
    mov ax, 0x01
    mov cx, 0x0000
    mov es, cx
    mov ecx, ebx
    mov bx, 0x8000
    mov edx, 0
    call LoadSector

    mov di, 0
    mov ax, 0x1000
    mov es, ax
    mov si, 0x8000
    inc si

    pop ebp
    add ebp, 2
    .loop3:

        mov ax, 0x01
        mov bx, di
        mov ecx, [si]
        add ecx, ebp
        xor edx, edx
        call LoadSector

        add di, 512
        inc si
        cmp byte [si], 0
        je .done2
        jmp .loop3

    .done2:
        ;lets jump to loader.bin.... finaly....
        ;lets jump 3... 2... 1...
        jmp 0x1000:0x0000 ;go!!!!!!

.halt:
    hlt
    jmp .halt

err:
    push errC
    call print
    add sp, 2
    mov ah, 0x0e
    add al, 0x30
    int 0x10
    jmp start.halt

NL:
    pusha

    ;getting the info
    mov ah, 03h
    mov bh, 0
    int 10h

    ;setting the info
    mov ah, 02h
    mov bh, 0
    inc dh
    xor dl, dl
    int 10h

    popa
    ret

print:
    push bp
    mov bp, sp
    push di
    push ax
    mov di, [bp+4]

    .loop:
        mov ah, 0x0e
        mov al, [di]
        cmp al, 0
        je .exit
        int 10h
        inc di
        jmp .loop
    .exit:
        pop ax
        pop di
        mov sp, bp
        pop bp
        ret

CmpStr:
    .loop:
        mov al, [si]
        mov ah, [di]
        cmp ah, al

        jne .exit

        inc si
        inc di

        mov al, [si]
        mov ah, [di]
        add ah, al

        cmp ah, 0

        je .quit
        jmp .loop

    .exit:
        xor ax, ax
        mov al, 1
        ret
    .quit:
        xor ax, ax
        mov al, 0
        ret

LoadSector:
    pusha
    mov word [DAP.S2R], ax
    mov word [DAP.DEA], bx
    mov word [DAP.DES], es
    mov dword [DAP.STAl], ecx
    mov dword [DAP.STAh], edx

    mov ah, 0x42
    mov dl, [DiskNo]
    mov si, DAP
    int 0x13
    mov al, 2
    jc err
    xor al, al
    popa
    ret

errC: db "Error Code: ", 0
loader: db "build/load.bin", 0
DiskNo: db 0
DAP:
    .pks: db 0x10
    .reserved: db 0x00
    .S2R: dw 0x0000 ;sectors to read
    .DEA: dw 0x0000  ;Ram Address
    .DES: dw 0x0000  ;Ram Segment
    .STAl: dd 0x00000000 ;Sector number low
    .STAh: dd 0x00000000 ;sector number high

times 446-($-$$) db 0
partition:
    part1:
        times 16 db 0
    part2:
        times 16 db 0
    part3:
        times 16 db 0
    part4:
        times 16 db 0

dw 0xaa55