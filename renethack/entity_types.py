import collections
from types import GeneratorType

from pygame.event import EventType

import renethack
from renethack.world_types import World
from renethack.util import validate

class Move:

    def __init__(self, direction: str) -> None:
        validate(self.__init__, locals())

        self.direction = direction

    def execute(self, world: World) -> None:
        validate(self.execute, locals())

class Wait:

    def execute(self, world: World) -> None:
        validate(self.execute, locals())

class Node:

    def __init__(self, parent: Node, point: tuple, target_point: tuple) -> None:
        validate(self.__init__, locals())

        self.parent = parent
        self.point = point

        self.calc_costs(target_point)

    def calc_costs(self, target_point: tuple) -> None:

        x, y = self.point
        target_x, target_y = target_point

        self.cost = 0 if parent is None else parent.cost + 1
        self.remaining_cost = abs(x - target_x) + abs(y - target_y)
        self.final_cost = self.cost + self.remaining_cost

class Monster:

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int) -> None:

        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength

        self.energy = 0
        self.icon_name = name

    def step(self, point: tuple, world: World) -> None:
        """Update this entity.

        May modify values within `level`.
        """
        validate(self.step, locals())

        if self.energy >= 100:
            # Calculate adjacent tile that is closest to hero and move
            # there.

            def adj_passable_nodes(node: Node) -> list:

                x, y = node.point

                adjacent = [
                    (x, y+1),
                    (x+1, y+1),
                    (x+1, y),
                    (x+1, y-1),
                    (x, y-1),
                    (x-1, y-1),
                    (x-1, y),
                    (x-1, y+1)
                    ]

                def valid_nodes() -> GeneratorType:

                    for adj_x, adj_y in adjacent:

                        tile = world.current_level.tiles[adj_x][adj_y]

                        if tile.entity is None and tile.type.passable:
                            yield Node(node, (adj_x, adj_y), world.hero)

                return list(valid_nodes())

            current_node = Node(None, current_point, world.hero)
            open_list = [current_node]
            closed_list = []

            while True:

                open_list.append(current_node)
                open_list.extend(adj_passable_nodes(current_node))
                open_list.remove(current_node)
                closed_list.append(current_node)

                open_list.sort(key=lambda n: n.final_cost)
                current_node = open_list[0]

        self.energy += self.speed

class Hero:

    def __init__(
            self,
            name: str,
            hit_points: int,
            defence: int,
            speed: int,
            strength: int) -> None:

        validate(self.__init__, locals())

        self.name = name
        self.hit_points = hit_points
        self.max_hit_points = hit_points
        self.defence = defence
        self.speed = speed
        self.strength = strength

        self.energy = 0
        self.actions = []
        self.icon_name = 'Hero'

    def path_to(self, world: World, point: tuple) -> None:
        pass

    def step(self, point: tuple, world: World) -> None:
        """Update this entity.

        May modify values within `world`.
        """
        validate(self.step, locals())

        if self.energy >= 100: 

            action = self.actions[0]
            self.actions = self.actions[1:]

            action.execute(world)

        self.energy += self.speed
