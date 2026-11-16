SECTIONS {
 . = 0x9ad000;
 .text : { *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 _end = .;
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
