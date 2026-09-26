import struct
import pathlib as pt

class util:
    def FindEmptyPart(MBR_TABLE: bytearray):

        partion = []
        partion.append(MBR_TABLE[0:16])
        partion.append(MBR_TABLE[16:32])
        partion.append(MBR_TABLE[32:48])
        partion.append(MBR_TABLE[48:64])

        for i in range(4):
            part = partion[i]
            id = part[4:5]
            if id == b'\x00':
                return i
        return -1

    def WriteBin(NoOfSectors, file, disk, Offset):

        with open(file, 'rb') as file, open(disk, 'r+b') as disk:
            data = file.read(NoOfSectors*512)
            disk.seek(Offset*512)
            disk.write(data)

    def FillZero(disk, size):
        """Size should be in sectors"""
        with open(disk, 'wb') as disk:
            disk.write(bytearray(size*1024))

    #AI
    def find_partition_range(
        disk_size_sectors: int, mbr_table_64bytes: bytes, required_sectors: int
        ) -> tuple[int, int] | None:
        """Finds a suitable starting and ending sector range for a new partition.

        :param disk_size_sectors: Total number of sectors available on the disk.
        :param mbr_table_64bytes: bytes object of exactly 64 bytes (4 MBR entries).
        :param required_sectors: Number of sectors needed for the new partition.
        :return: A tuple of (start_sector, end_sector) inclusive, or None if no space.
        """
        if len(mbr_table_64bytes) != 64:
            raise ValueError("MBR table must be exactly 64 bytes.")

        partitions = []

        # Parse the 4 partition entries (16 bytes each)
        for i in range(4):
            entry_offset = i * 16
            entry = mbr_table_64bytes[entry_offset : entry_offset + 16]

            # Bytes 8-11: Starting LBA (Little-endian 32-bit unsigned int)
            # Bytes 12-15: Sector count (Little-endian 32-bit unsigned int)
            start_lba = struct.unpack("<I", entry[8:12])[0]
            num_sectors = struct.unpack("<I", entry[12:16])[0]

            if num_sectors > 0:
                end_lba = start_lba + num_sectors - 1
                partitions.append((start_lba, end_lba))

        # Sort existing partitions by their starting LBA
        partitions.sort(key=lambda x: x[0])

        # Standard MBR starts partition allocation after sector 0 (the MBR boot sector)
        current_start = 1

        # Check for gaps between existing partitions
        for p_start, p_end in partitions:
            if p_start > current_start:
                gap_size = p_start - current_start
                if gap_size >= required_sectors:
                    return (current_start, current_start + required_sectors - 1)
            current_start = max(current_start, p_end + 1)

        # Check if there is enough space after the last partition
        if disk_size_sectors - current_start >= required_sectors:
            return (current_start, current_start + required_sectors - 1)

        return None  # No suitable range found

def CreateSFS2(Size: int, Lable: str, file: str):

    """Enter size in 4KiB Clusters."""

    MBR = 446 #MBR entry offset

    with open(file, 'r+b') as disk:

        ByteOrder = 'little' #GLobal ByteOrder Var
        
        disk.seek(MBR) 
        MBR_TABLE = disk.read(64) #reading the MBR
        
        partNO = util.FindEmptyPart(MBR_TABLE) #function to find an empty par
        #if part == -1 there is no partion left to occupy
        if partNO == -1:
            print("No partition left to occupy on disk.")
            return 0

        #the details of SFS2, we use 0x6F as our partition ID

        Status =        bytes.fromhex('80')
        StartingCHS =   bytes.fromhex('000000')
        PartitionType = bytes.fromhex('6F')
        EndingCHS =     bytes.fromhex('000000')
        StartingLBA =   bytes.fromhex('00000000')
        totalSectors =  int.to_bytes(Size*4, 4, ByteOrder)

        #Seeking to the end of the file/Stream and geting the offset to get the size in bytes
        disk.seek(0, 2)
        disk_size = disk.tell()

        RANGE_DATA = util.find_partition_range(disk_size, MBR_TABLE, Size*4) #Geting the starting and ending of required rang

        if RANGE_DATA == None: #if RANGE_DATA == None then no range was found fulfing the criterias
            print("Not enough space on disk")
            print(MBR_ENTRY, RANGE_DATA, disk_size)
            return 0
        
        StartingLBA = int.to_bytes(RANGE_DATA[0] , 4, ByteOrder)

        #Writing back the INFO
        MBR_ENTRY = Status+StartingCHS+PartitionType+EndingCHS+StartingLBA+totalSectors
        disk.seek(446)
        disk.seek(partNO*16, 1)
        disk.write(MBR_ENTRY)

        #Filing the SFS2 partiton data
        #the length in MBR and root table are in 512byte but the file and pointers and diskmap will assume in 4KiB clusters
        disk.seek(RANGE_DATA[0]*512)
        disk.write(str.encode(Lable[0:16], 'utf-8'))
        disk.seek(RANGE_DATA[0]*512)
        disk.seek(25, 1)
        disk.write(int.to_bytes(Size*8, 4, ByteOrder))

        NoOfBytesNeededToMapPartition = int(((Size+8-1)/8)) #Geting how many bytes to map Size number of clusters in BitMap
        tmp = bytearray(NoOfBytesNeededToMapPartition)
        disk.seek(RANGE_DATA[0]*512+4096)
        disk.write(tmp)

def WriteFile(filename, disk):
    pass

util.FillZero('disk.img', 64)
util.WriteBin(5, 'build/boot.bin', 'disk.img', 0)
CreateSFS2(9, "TOS_SYS", 'disk.img')