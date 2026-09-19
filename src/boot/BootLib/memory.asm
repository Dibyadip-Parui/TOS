bits 16

GetMemMap:
    push bp
    mov bp, sp
    pusha

    .loop:

    popa
    mov sp, bp
    pop bp
    ret