import os
import pathlib as pt
import struct
from sfs1 import WriteFile

class util:
    def DivideStream(data: bytearray, chunk_size: int = 512) -> list[bytearray]:
        """Splits a bytearray into a list of fixed-size bytearray chunks."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    import struct
    def find_partition_slot(mbr_table_64bytes: bytearray, required_sectors: int) -> tuple[int, int]:
        """Finds the first available LBA range that can fit the required number of sectors."""
        partitions = []
        
        for i in range(4):
            entry_offset = i * 16
            entry = mbr_table_64bytes[entry_offset : entry_offset + 16]
            
            part_type = entry[4]
            if part_type == 0:
                continue
                
            start_lba = struct.unpack("<I", entry[8:12])[0]
            num_sectors = struct.unpack("<I", entry[12:16])[0]
            
            if num_sectors > 0:
                partitions.append((start_lba, start_lba + num_sectors))

        # Sort active partitions by their starting LBA
        partitions.sort(key=lambda x: x[0])
        
        # Check for gaps starting from LBA 1 (right after the MBR sector)
        search_start = 1
        for start, end in partitions:
            if start - search_start >= required_sectors:
                return (search_start, required_sectors)  # Fits in a gap
            search_start = max(search_start, end)
            
        # If no intermediate gap is large enough, allocate it right after the last partition
        return (search_start, required_sectors)

    # Example usage:
    # mbr_64byte = bytearray(64)
    # slot_start, slot_sectors = find_partition_slot(mbr_64byte, required_sectors=2048)
    # print(f"Can create partition at LBA {slot_start} with length {slot_sectors}")


def CreatePartition(Lable: str, Size: int, Disk):
    try:
        with open(Disk, 'r+b') as disk:
            disk.seek(446)
            table = bytearray(disk.read(64))

            part0 = table[0:16]
            part1 = table[16:32]
            part2 = table[32:48]
            part3 = table[48:64]

            PartNo = 0
            data = bytearray(16)

            if part0[4:5] == bytes.fromhex('00'):
                PartNo = 0
                data = part0
            elif part1[4:5] == bytes.fromhex('00'):
                PartNo = 1
                data = part1
            elif part2[4:5] == bytes.fromhex('00'):
                PartNo = 2
                data = part2
            elif part3[4:5] == bytes.fromhex('00'):
                PartNo = 3
                data = part3

            data[0:1] = bytes.fromhex('80')
            data[4:5] = bytes.fromhex('5F')
            a = util.find_partition_slot(table, Size*2)
            starting = a[0]
            #print((hex(starting).split('x')[0]))
            data[8:12] = starting.to_bytes(4, byteorder='little')
            data[12:16] = int.to_bytes(Size*2, 4, 'little')

            disk.seek(446)
            disk.seek(PartNo*16, 1)
            disk.write(data)

            disk.seek(starting*512)
            disk.seek(512, 1)
            a = bytearray(512)
            disk.write(a)

            disk.seek(starting*512)
            disk.write(bytes(Lable[0:16], 'utf-8'))
            disk.seek(starting*512)
            disk.seek(16, 1)
            

    except FileNotFoundError as e:
        print(e)

    return 0
def WriteDisk(filename, input, NoOfSector, offset):
    size = NoOfSector*512
    offset = offset*512
    try:
        with open(filename, 'r+b') as disk, open(input, 'rb') as file:
            data = file.read(size)
            disk.seek(offset, 0)
            disk.write(data)
    except FileNotFoundError as error:
        print("File Not Found: ", error)
def truncate(filename, NoOfSectors):
    """Enter NoOfSectors in KiB"""
    size = NoOfSectors*1024
    try:
        with open(filename, 'wb') as disk:
            data = bytearray(size)
            disk.write(data)
    except FileNotFoundError as error:
        print(error)


truncate('disk/disk.img', 64)
WriteDisk('disk/disk.img', 'build/boot.bin', 1, 0)
CreatePartition("TOS", 8, 'disk/disk.img')
WriteFile('build/load.bin', 'disk/disk.img', 0)