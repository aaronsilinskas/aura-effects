class Palette:
    @staticmethod
    def pack_rgb(r: int, g: int, b: int) -> int:
        return (r << 16) | (g << 8) | b

    def lookup(self, value: float) -> int:
        raise NotImplementedError("Palette implementations must implement lookup()")


class PaletteLUT256(Palette):
    __slots__ = ("colors",)

    def __init__(self, packed_palette: bytes):
        self.colors: list[int] = PaletteLUT256._build_lookup(packed_palette)

    @staticmethod
    def _build_lookup(packed_palette: bytes) -> list[int]:
        if len(packed_palette) == 0:
            return [0] * 256
        if len(packed_palette) % 4 != 0:
            raise ValueError("Packed palette length must be a multiple of 4")

        source_palette = packed_palette[:]
        if source_palette[0] != 0:
            source_palette = bytes([0, 0, 0, 0]) + source_palette
        if source_palette[-4] != 255:
            source_palette = source_palette + bytes([255, 0, 0, 0])

        lookup_palette: list[int] = [0] * 256

        for source_index in range(0, len(source_palette) - 4, 4):
            start_index = source_palette[source_index]
            start_r = source_palette[source_index + 1]
            start_g = source_palette[source_index + 2]
            start_b = source_palette[source_index + 3]

            lookup_palette[start_index] = Palette.pack_rgb(start_r, start_g, start_b)

            end_index = source_palette[source_index + 4]
            end_r = source_palette[source_index + 5]
            end_g = source_palette[source_index + 6]
            end_b = source_palette[source_index + 7]

            # set all colors between start and end to a weighted blend of the two
            for i in range(start_index + 1, end_index):
                weight = (i - start_index) / (end_index - start_index)
                r = int(start_r + weight * (end_r - start_r))
                g = int(start_g + weight * (end_g - start_g))
                b = int(start_b + weight * (end_b - start_b))
                lookup_palette[i] = Palette.pack_rgb(r, g, b)

        lookup_palette[255] = Palette.pack_rgb(
            source_palette[-3], source_palette[-2], source_palette[-1]
        )

        return lookup_palette

    def lookup(self, value: float) -> int:
        if value <= 0.0:
            return self.colors[0]
        if value >= 1.0:
            return self.colors[255]

        index = int(value * 255.0)
        return self.colors[index]
