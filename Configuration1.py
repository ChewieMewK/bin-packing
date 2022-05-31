from Rect import Rect
from Point import Point, PointType

class Configuration:

    # The amount to look in each direction when determining if a corner is concave
    eps = 0.001

    def __init__(self, size: Point, all_rects: list, packed_rects: list[Rect] = []) -> None:
        self.size = size
        
        self.all_rects = all_rects
        self.unpacked_rects = all_rects
        self.packed_rects = packed_rects

        self.generate_L()


    def generate_L(self):
        # 1. concave corners
        concave_corners = self.get_concave_corners()

        # 2. generate ccoas for every rect
        ccoas: list[Rect] = []
        for x, y in self.unpacked_rects:
            for corner, type in concave_corners:
                for rotated in [False, True]:
                    ccoa = Rect(corner, x, y, type, rotated)

                    # 3. Add if it fits
                    if not self.fits(ccoa):
                        continue
                    ccoas.append(ccoa)

        self.L = ccoas

    def get_concave_corners(self) -> list[tuple[Point,PointType]]:
        concave_corners: list[tuple(Point,PointType)] = []

        for corner in self.get_all_corners():
            corner_type = self.get_corner_type(corner)
            if corner_type:
                concave_corners.append((corner,corner_type))

        return concave_corners

    def get_corner_type(self, p: Point) -> bool:
        checks = self.check_boundaries(p)
        if sum(checks) == 3:
            index = [i for i, x in enumerate(checks) if not x][0]
            return PointType(index)
        return None

    def check_boundaries(self, p: Point):
        return [
            self.contains(Point(p.x+self.eps, p.y+self.eps)),
            self.contains(Point(p.x-self.eps, p.y+self.eps)),
            self.contains(Point(p.x+self.eps, p.y-self.eps)),
            self.contains(Point(p.x-self.eps, p.y-self.eps))
        ]

    def contains(self, point: Point) -> bool:
        # Return true if point is out of bounds
        if point.x <= 0 or point.y <= 0 or self.size.x <= point.x or self.size.y <= point.y:
            return True
        
        # Check if any of the packed rects contain the point
        for r in self.packed_rects:
            if r.contains(point):
                return True
        return False


    def fits(self, ccoa: Rect) -> bool:
        """
        Returns true if a given ccoa fits into the configuration without overlapping any of the rects
        or being out of bounds
        """
        # Check if the ccoa is out of bounds in any way
        if ccoa.origin.x < 0 or ccoa.origin.y < 0 or self.size.x < ccoa.origin.x + ccoa.width or self.size.y < ccoa.origin.y + ccoa.height:
            return False
        
        # Check if the rect overlaps any of the already packed rects
        for rect in self.packed_rects:
            if ccoa.overlaps(rect):
                return False
        return True


    def place_rect(self, rect: Rect) -> None:
        # Add rect to packed rects
        self.packed_rects.append(rect)

        # Remove the rect from unpacked rects
        if (rect.width,rect.height) in self.unpacked_rects:
            self.unpacked_rects.remove((rect.width,rect.height))
        elif (rect.height, rect.width) in self.unpacked_rects:
            self.unpacked_rects.remove((rect.height, rect.width))

        self.generate_L() # TODO: Do somehing like passing the just placed rect for more efficiency

    def density(self) -> float:
        """
        Return the percentage of total container area filled by packed rects
        """
        total_area = self.size.x * self.size.y
        occupied_area = sum([x.area() for x in self.packed_rects])

        return occupied_area/total_area

    def get_all_corners(self) -> list[Point]:
        """
        Returns a set of all unique points in the container
        """
        # The container corners
        corners = [Point(0,0), Point(0,self.size.y), Point(self.size.x,0), self.size]

        # Get corners for every rect
        for rect in self.packed_rects:
            corners += [rect.corner_bot_l, rect.corner_bot_r, rect.corner_top_l, rect.corner_top_r]
        return list(set(corners))

    def is_successful(self) -> bool:
        return len(self.unpacked_rects) == 0