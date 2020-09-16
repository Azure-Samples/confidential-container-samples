from cffi import FFI
ffi = FFI()
ffi.cdef("""
int scone_sgx_report_get(
    const unsigned char *report_data, 
    const unsigned char *target_info,
    unsigned char *report);
""")
C = ffi.dlopen(None)

report = ffi.new("unsigned char[]", 10000)
res = C.scone_sgx_report_get(None, None, report)
print(res)
print(report)
