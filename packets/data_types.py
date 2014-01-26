from construct import Construct, Struct, Enum, Byte, Switch, BFloat64, Flag, \
    Array, LazyBound, Field
from construct.core import _read_stream, _write_stream


class SignedVLQ(Construct):
    def _parse(self, stream, context):
        value = 0
        while True:
            tmp = ord(_read_stream(stream, 1))
            value = (value << 7) | (tmp & 0x7f)
            if tmp & 0x80 == 0:
                break
        if (value & 1) == 0x00:
            return value >> 1
        else:
            return -(value >> 1)

    def _build(self, obj, stream, context):
        value = abs(obj * 2)
        if obj < 0:
            value += 1
        VLQ("")._build(value, stream, context)


class VLQ(Construct):
    def _parse(self, stream, context):
        value = 0
        while True:
            tmp = ord(_read_stream(stream, 1))
            value = (value << 7) | (tmp & 0x7f)
            if tmp & 0x80 == 0:
                break
        return value

    def _build(self, obj, stream, context):
        result = bytearray()
        value = int(obj)
        while value > 0:
            byte = value & 0x7f
            value >>= 7
            if value != 0:
                byte |= 0x80
            result.insert(0, byte)
        if len(result) > 1:
            result[0] |= 0x80
            result[-1] ^= 0x80
        _write_stream(stream, len(result), "".join([chr(x) for x in result]))


class StarString(Construct):
    def _parse(self, stream, context):
        l = VLQ("").parse_stream(stream)
        return _read_stream(stream, l)

    def _build(self, obj, stream, context):
        out = VLQ("").build(len(unicode(obj)))+obj
        print out.encode("hex")
        _write_stream(stream, len(out), out)

variant_variant = Struct("data",
                         VLQ("length"),
                         Array(lambda ctx: ctx.length,
                         LazyBound("data",
                         lambda: variant())))

dict_variant = Struct("data",
                      VLQ("length"),
                      Array(lambda ctx: ctx.length,
                            Struct("dict",
                                   StarString("key"),
                                   LazyBound("value", lambda: variant()))))

variant = lambda name="variant": Struct(name,
                                        Enum(Byte("type"),
                                             NULL=1,
                                             DOUBLE=2,
                                             BOOL=3,
                                             SVLQ=4,
                                             STRING=5,
                                             VARIANT=6,
                                             DICT=7
                                        ),
                                        Switch("data", lambda ctx: ctx.type,
                                               {
                                                   "DOUBLE": BFloat64("data"),
                                                   "BOOL": Flag("data"),
                                                   "SVLQ": SignedVLQ("data"),
                                                   "STRING": StarString(
                                                       "data"),
                                                   "VARIANT": variant_variant,
                                                   "DICT": dict_variant
                                               },
                                               default=Field("null", 0)))