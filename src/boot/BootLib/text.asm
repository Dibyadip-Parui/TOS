bits 16

print:
    push bp
    mov bp, sp
    pusha

    mov di, [bp+2]
    .loop:
        mov ah, 0x0e
        mov al, [di]
        int 10h

        inc di
        cmp byte [di], 0
        je .done
        jmp .loop

    .done:
    popa
    pop bp
    ret