#pragma author Dobby233Liu
#pragma description Arc System Works Rockin' Pretty archive
#pragma endian little

struct file<auto data_start> {
    char name[64];
    u32 size_uncompressed;
    u32 size_compressed;
    u32 data_offset;
    u8 data[size_compressed] @ data_start + data_offset;
} [[name(name)]];

struct ArcSysHSBArchive {
    u16 version_maybe;
    u16 file_count;
    u32 data_start;
    file<data_start> files[file_count];
};

ArcSysHSBArchive archive @ 0x00;