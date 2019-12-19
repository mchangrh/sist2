mimes = {}
noparse = set()
ext_in_hash = set()

major_mime = {
    "model": 1,
    "example": 2,
    "message": 3,
    "multipart": 4,
    "font": 5,
    "video": 6,
    "audio": 7,
    "image": 8,
    "text": 9,
    "application": 10,
    "x-epoc": 11,
}

pdf = (
    "application/pdf",
    "application/x-cbz",
    "application/epub+zip",
    "application/vnd.ms-xpsdocument",
)

font = (
    "application/vnd.ms-opentype",
    "application/x-ms-compress-szdd"
    "application/x-font-sfn",
    "application/x-font-ttf",
    "font/otf",
    "font/sfnt",
    "font/woff",
    "font/woff2"
)

# Archive "formats"
archive = (
    "application/x-tar",
    "application/zip",
    "application/x-rar",
    "application/x-arc",
    "application/x-warc",
    "application/x-7z-compressed",
)

# Archive "filters"
arc_filter = (
    "application/gzip",
    "application/x-bzip2",
    "application/x-xz",
    "application/x-zstd",
    "application/x-lzma",
    "application/x-lz4",
    "application/x-lzip",
    "application/x-lzop",
)

doc = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)

cnt = 1


def mime_id(mime):
    global cnt
    major = mime.split("/")[0]
    mime_id = str((major_mime[major] << 16) + cnt)
    cnt += 1
    if mime in noparse:
        mime_id += " | 0x80000000"
    elif mime in pdf:
        mime_id += " | 0x40000000"
    elif mime in font:
        mime_id += " | 0x20000000"
    elif mime in archive:
        mime_id += " | 0x10000000"
    elif mime in arc_filter:
        mime_id += " | 0x08000000"
    elif mime in doc:
        mime_id += " | 0x04000000"
    elif mime == "application/x-empty":
        return "1"
    return mime_id


def clean(t):
    return t.replace("/", "_").replace(".", "_").replace("+", "_").replace("-", "_")


with open("mime.csv") as f:
    for l in f:
        mime, ext_list = l.split(",")
        if l.startswith("!"):
            mime = mime[1:]
            noparse.add(mime)
        ext = [x.strip() for x in ext_list.split("|")]
        mimes[mime] = ext

    print("// **Generated by mime.py**")
    print("#ifndef MIME_GENERATED_C")
    print("#define MIME_GENERATED_C")
    print("#include <glib-2.0/glib.h>\n")
    print("#include <stdlib.h>\n")
    # Enum
    print("enum mime {")
    for mime, ext in sorted(mimes.items()):
        print("    " + clean(mime) + "=" + mime_id(mime) + ",")
    print("};")

    # Enum -> string
    print("char *mime_get_mime_text(unsigned int mime_id) {"
          "switch (mime_id) {")
    for mime, ext in mimes.items():
        print("case " + clean(mime) + ": return \"" + mime + "\";")
    print("default: return NULL;}}")

    # Ext -> Enum
    print("GHashTable *mime_get_ext_table() {"
          "GHashTable *ext_table = g_hash_table_new(g_str_hash, g_str_equal);")
    for mime, ext in mimes.items():
        for e in [e for e in ext if e]:
            print("g_hash_table_insert(ext_table, \"" + e + "\", (gpointer)" + clean(mime) + ");")
            if e in ext_in_hash:
                raise Exception("extension already in hash: " + e)
            ext_in_hash.add(e)
    print("return ext_table;}")

    # string -> Enum
    print("GHashTable *mime_get_mime_table() {"
          "GHashTable *mime_table = g_hash_table_new(g_str_hash, g_str_equal);")
    for mime, ext in mimes.items():
        print("g_hash_table_insert(mime_table, \"" + mime + "\", (gpointer)" + clean(mime) + ");")
    print("return mime_table;}")
    print("#endif")
