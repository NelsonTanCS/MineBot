"""Contains command for $minesweeper."""
import json
from random import randint, uniform
import asyncio
import numpy as np
import discord


class Client(discord.Client):
    async def on_ready(self):

        print("")
        print(f"Logged in as: {self.user.name}")
        print("")

    async def on_message(self, message):
        pass


class MineBot(Client):
    async def on_message(self, message):

        if message.content == "$minesweeper":
            await self.minesweeper(message)

    async def minesweeper(self, message):
        """Command that generates minesweepers to repel the user's boredom."""
        embed, minesweep = await self.setup_minesweep(message)
        canceled, mine_error, values = await self.get_all_fields(
            message, embed, minesweep)

        mine_error = await self.delete_error(mine_error)
        await minesweep.delete()
        if not canceled:
            await self.minesweep_create(message, values["Size"],
                                        values["Difficulty"])
        else:
            await message.channel.send(embed=self.canceled_embed())

    async def get_all_fields(self, message, embed, minesweep):
        """Help function that calls get_field for all fields."""
        canceled = False
        mine_error = None
        parameter_dict = {
            "Size":
            "Enter a size from: `6 - 32`, or put 0 for a random size",
            "Difficulty":
            "Enter a difficulty from: `1 - 10`, or put 0 for a random difficulty",
        }
        values = {"Size": None, "Difficulty": None}

        for key, value in parameter_dict.items():
            for_items = {"key": key, "value": value}

            if canceled:
                break

            embed.title = f"What do you want the {key.lower()}?"
            embed.set_footer(text=value)
            await minesweep.edit(embed=embed)

            canceled, mine_error, values = await self.get_field(
                message, for_items, mine_error, values)

        return canceled, mine_error, values

    async def get_field(self, message, for_items, mine_error, values):
        """Help function that gets a field at each for_items["key"]."""
        reply = await self.wait_msg_or_react(message)
        canceled = self.check_canceled(reply)
        if not canceled:
            mine_error = await self.delete_error(mine_error)
            reply.content = Map.check_minesweep(
                reply.content, parameter=for_items["key"].lower())
            await reply.delete()
            if reply.content:
                values[for_items["key"]] = reply.content

            else:
                error_embed = discord.Embed(
                    title=f"Error: Invalid {for_items['key']}",
                    description=for_items["value"],
                    color=0x9E1818,
                )
                mine_error = await reply.channel.send(embed=error_embed)
                canceled, mine_error, values = await self.get_field(
                    message, for_items, mine_error, values)
        return canceled, mine_error, values

    async def wait_msg_or_react(self, message):
        """
        Wait for a message or reaction.

        Parameters:
            message, client: the discord message and client objects respectively
        Returns:
            reply: discord message object with reply, None if timeout error.

        """

        def reply_check(mess):
            """Check if it is a valid reply."""
            return mess.author == message.author and mess.channel == message.channel

        def react_check(reaction, user):
            """Check if it is a valid react."""
            return user == message.author and str(reaction.emoji) == '❌'

        try:
            done, pending = await asyncio.wait(
                [
                    self.wait_for("message", timeout=60, check=reply_check),
                    self.wait_for("reaction_add", check=react_check),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            reply = done.pop().result()
        except asyncio.TimeoutError:
            reply = None
        finally:
            for rest in pending:
                rest.cancel()
        return reply

    @staticmethod
    async def setup_minesweep(message):
        """Help function that sets up minesweper and returns embed and message used."""
        embed = discord.Embed(color=0xC27C0E)
        embed.set_author(name="💣 Minesweeper!")
        minesweep = await message.channel.send(embed=embed)
        await minesweep.add_reaction('❌')
        return embed, minesweep

    @staticmethod
    async def minesweep_create(message, size, diff):
        """Help function that creates the minesweeper with a size and difficulty."""
        map = Map(size, diff)
        map.create_map()
        map.set_bombs()
        text_board = map.convert_to_text(map.board)
        if len(text_board) >= 2000:
            split_num = (np.ceil(len(text_board) / 2000)) + 1
            splits = np.array_split(map.board, split_num)
            for split in splits:
                text = map.convert_to_text(split)
                try:
                    await message.channel.send(text)
                except discord.errors.HTTPException:
                    for s_text in text.splitlines():
                        await message.channel.send(s_text)
        else:
            await message.channel.send(text_board)

    @staticmethod
    async def delete_error(error):
        """Delete error if it exists."""
        if error:
            await error.delete()
            error = None
        return error

    @staticmethod
    def check_canceled(reply):
        """Check if a reply is saying to cancel."""
        return (isinstance(reply, tuple)
                and reply[0].emoji == '❌') or reply is None

    @staticmethod
    def canceled_embed():
        """Return canceled embed."""
        embed = discord.Embed(color=0x9E1818)
        embed.set_author(name="Canceled")
        return embed


class Map:
    """Map class for creating minesweepers."""

    def __init__(self, size, difficulty):
        """Set the size and difficulty of the map."""
        self.size = size
        self.difficulty = (np.cbrt(difficulty)) * 0.8
        self.board = None

    def create_map(self):
        """Create the board."""
        self.board = np.zeros((self.size, self.size), dtype=int)
        return self.board

    def set_bombs(self):
        """Place the bombs."""
        bombs = self.prob_round(self.size * (self.difficulty + 1))
        placed = 0
        while placed < bombs:
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)
            if not self.board[x][y] >= 9:
                self.board[x][y] = 9
                self.set_numbers(x, y)
                placed += 1
        return self.board

    def set_numbers(self, x, y):
        """Set the numbers around the bomb."""
        if x < self.size and y < self.size and self.board[x][y] >= 9:
            for i in range(9):
                try:
                    f = x - 1 + i % 3
                    h = y - 1 + int(i / 3)

                    if self.board[f, h] < 9 and abs(f) == f and abs(h) == h:
                        self.board[f, h] += 1
                except IndexError:
                    pass

    @staticmethod
    def convert_to_text(board):
        """Convert the map array to text."""
        text_key = {
            0: "||:white_large_square:|| ",
            1: "||:one:|| ",
            2: "||:two:|| ",
            3: "||:three:|| ",
            4: "||:four:|| ",
            5: "||:five:|| ",
            6: "||:six:|| ",
            7: "||:seven:|| ",
            8: "||:eight:|| ",
            9: "||:bomb:|| ",
        }
        text_board = board.astype(object)
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                text_board[x, y] = text_key[board[x, y]]
        text_board = "\n".join("".join((el) for el in inner)
                               for inner in text_board)
        return text_board

    @staticmethod
    def prob_round(_input):
        """Round up or down based on probability."""
        dice = uniform(0, 1)
        try:
            base = int(_input)
            thresh = _input - base
            if dice >= thresh:
                output = int(_input)
            elif dice <= thresh:
                output = int(_input) + 1

        except ValueError:
            return "Error! Value given is not a number!"
        return output

    @staticmethod
    def check_minesweep(num, parameter):
        """Check if the parameter is valid."""
        try:
            num = int(num)
        except (TypeError, ValueError):
            return None

        if parameter == "size":
            if 6 <= num <= 32:
                output = num
            elif num == 0:
                output = randint(6, 32)
            else:
                output = None
        elif parameter == "difficulty":
            if 1 <= num <= 10:
                output = num / 10
            elif num == 0:
                output = randint(1, 10) / 10
            else:
                output = None
        return output


def main():
    with open("config.json", "r") as infile:
        config = dict(json.load(infile))
        token = config["token"]

    client = MineBot()
    client.run(token)


if __name__ == '__main__':
    main()
