import struct
from pathlib import Path

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

def FindFreeSector(Table: bytearray, size)->list:

    Table = bytearray(Table)
    sector = []
    for i in range(256):
        sector.append(Table[i])
    if size>256:
        print("File too big, size: ", size)
        return []
    selected = []
    for i in range(256):
        if sector[i] == 0:
            size = size-1
            Table[i] = 1
            selected.append(i)

        if size == 0:
            return selected, Table
            break
    
    if size != 0:
        print("Not Enough space on partiton.")
        return []

def WriteFile(filename, Disk, PartNo):

    if PartNo > 4:
        print("The MBR can not have more than 4 partition the count starts from 0.")
    else:
        with open(Disk, 'r+b') as disk, open(filename, 'rb') as file:

            disk.seek(446)
            disk.seek(PartNo*16, 1)
            MBR = disk.read(16)
            data = file.read()

            if hex(MBR[4]) == '0x5f':

                PartitionStart = int.from_bytes(MBR[8:11], 'little')

                disk.seek(PartitionStart*512)
                disk.seek(16, 1)

                NoOfEntries = int.from_bytes(disk.read(4), 'little')
                NoOfEntries += 1

                disk.seek(PartitionStart*512)
                disk.seek(16, 1)
                disk.write(int.to_bytes(NoOfEntries, 4, 'little'))

                disk.seek((PartitionStart+1)*512)
                DiskMap = disk.read(512)
                data = util.DivideStream(data, 512)
                sectors, DiskMap = FindFreeSector(DiskMap, len(data)+1)

                if sectors == []:
                    print("Not enough space.")
                else:


                    FileEntry = bytearray(32)
                    name = filename

                    nameB = bytes(name, 'utf-8')[:26].ljust(26, b'\x00')

                    FileEntry[0:25] = nameB
                    FileEntry[30] = sectors[0]
                    FileEntry[31] = len(sectors)

                    disk.seek(PartitionStart*512)
                    disk.seek(32, 1)
                    disk.seek((NoOfEntries-1)*32, 1)
                    disk.write(FileEntry)

                    #generating the pointer table
                    pT = bytearray(512)
                    for i in range(len(sectors)):
                        pT[i] = sectors[i]

                    data.insert(0, pT)

                    for i in range(len(sectors)):
                        disk.seek((PartitionStart+1)*512)
                        disk.seek((sectors[i]+1)*512, 1)
                        print(hex(disk.tell()))
                        disk.write(data[i])

                    disk.seek((PartitionStart+1)*512)
                    disk.write(DiskMap)
                    print("Written file: ", filename, ' to disk: ', Disk)
            else:
                print("The partiton number: ", PartNo, " Is not valid SFS1 partition.")