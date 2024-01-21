from discord.ext.commands import Bot, Context, check, command
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from discord_bots.checks import is_admin
from discord_bots.cogs.base import BaseCog
from discord_bots.models import Map, Queue, Rotation, RotationMap


class RotationCog(BaseCog):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    @command()
    @check(is_admin)
    async def addrotation(self, ctx: Context, rotation_name: str):
        session = ctx.session

        try:
            session.add(Rotation(name=rotation_name))
            session.commit()
        except IntegrityError:
            session.rollback()
            await self.send_error_message(
                f"Error adding rotation {rotation_name}). Does it already exist?"
            )
        else:
            await self.send_success_message(f"{rotation_name} added to rotation pool")

    @command(usage="<rotation_name> <map_short_name> <position>")
    @check(is_admin)
    async def addrotationmap(
        self, ctx: Context, rotation_name: str, map_short_name: str, ordinal: int
    ):
        session = ctx.session

        if ordinal < 1:
            await self.send_error_message("Position must be a positive number")
            return

        try:
            rotation = (
                session.query(Rotation).filter(Rotation.name.ilike(rotation_name)).one()
            )
        except NoResultFound:
            await self.send_error_message(f"Could not find rotation: {rotation_name}")
            return

        try:
            map = session.query(Map).filter(Map.short_name.ilike(map_short_name)).one()
        except NoResultFound:
            await self.send_error_message(f"Could not find map: {map_short_name}")
            return

        # logic for organizing ordinals.  ordinals are kept unique and consecutive.
        # we insert a map directly at an ordinal and increment every one after that.
        rotation_maps = (
            session.query(RotationMap)
            .join(Rotation, RotationMap.rotation_id == rotation.id)
            .order_by(RotationMap.ordinal.asc())
            .all()
        )

        if ordinal > len(rotation_maps):
            ordinal = len(rotation_maps) + 1
        else:
            for rotation_map in rotation_maps[ordinal - 1 :]:
                rotation_map.ordinal += 1

        try:
            session.add(
                RotationMap(rotation_id=rotation.id, map_id=map.id, ordinal=ordinal)
            )
            session.commit()
        except IntegrityError:
            session.rollback()
            await self.send_error_message(
                f"Error adding {map_short_name} to {rotation_name} at position {ordinal}"
            )
        else:
            await self.send_success_message(
                f"{map.short_name} added to {rotation.name} at position {ordinal}"
            )

    @command()
    async def listrotations(self, ctx: Context):
        session = ctx.session

        data = (
            session.query(Rotation.name, RotationMap.ordinal, Map.short_name)
            .outerjoin(RotationMap, Rotation.id == RotationMap.rotation_id)
            .outerjoin(Map, Map.id == RotationMap.map_id)
            .order_by(RotationMap.ordinal.asc())
            .all()
        )

        grouped_data = {}
        for row in data:
            if row[0] in grouped_data:
                grouped_data[row[0]].append(row[2])
            elif not row[2]:
                grouped_data[row[0]] = ["--No Maps--"]
            else:
                grouped_data[row[0]] = [row[2]]

        output = ""
        for key, value in grouped_data.items():
            output += f"**- {key}**"
            output += f"_{', '.join(value)}_\n\n"

        await self.send_info_message(output)

    @command()
    async def setqueuerotation(self, ctx: Context, queue_name: str, rotation_name: str):
        session = ctx.session

        try:
            queue = session.query(Queue).filter(Queue.name.ilike(queue_name)).one()
        except NoResultFound:
            await self.send_error_message(f"Could not find queue: {queue_name}")
            return

        try:
            rotation = (
                session.query(Rotation).filter(Rotation.name.ilike(rotation_name)).one()
            )
        except NoResultFound:
            await self.send_error_message(f"Could not find rotation: {rotation_name}")
            return

        queue.rotation_id = rotation.id
        session.commit()
        await self.send_success_message(
            f"Rotation for {queue.name} set to {rotation.name}"
        )
