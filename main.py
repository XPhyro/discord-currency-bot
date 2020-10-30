from config import *
from forex_python.converter import CurrencyRates as cr
from secrets import *
import asyncio
import datetime as dt
import discord


def get_rate():
    #return "%.7f" % cr().get_rate(CURRENCY_ORIG_CODE, CURRENCY_DEST_CODE)
    return str(cr().get_rate(CURRENCY_ORIG_CODE, CURRENCY_DEST_CODE))


def get_short_rate():
    return "%.2f" % cr().get_rate(CURRENCY_ORIG_CODE, CURRENCY_DEST_CODE)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def update_presence(self):
        print("Updating presence.")
        await self.change_presence(
            activity=discord.Streaming(
                name=(DISCORD_PRESENCE_STREAM_NAME.format(get_short_rate())),
                url=DISCORD_PRESENCE_STREAM_URL,
            )
        )

    async def on_ready(self):
        print(f"Logged in as\n{self.user.name}\n{self.user.id}\n")
        await self.update_presence()

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith(DISCORD_PREFIX):
            q = str(message.author.mention)
            args = [i.lower().replace("ı", "i") for i in message.content.split()[1:]]

            if len(args) == 0:
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(f"Ben Berat Albayrak {q}.")
                return

            if args[0] == "yardim":
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(DISCORD_HELP_MESSAGE.format(q))
            elif args[0] == "etiket":
                if message.channel.id != DISCORD_CHANNEL_ID:
                    await message.channel.send(
                        f"Bu kanaldan etiket listesine ekleyemem {q}."
                    )
                    return
                with open(MENTIONS_FILENAME, "r") as f:
                    r = f.readlines()
                if q + "\n" in r:
                    print(f"Removing {q} from mention list.")
                    r.remove(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Etiket listesinden çıkarıldın {q}.")
                else:
                    print(f"Adding {q} to mention list.")
                    r.append(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Etiket listesine eklendin {q}.")
            else:
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(
                    f"Değerli vatandaşım, lütfen özrümü kabul edin, dediğinizi anlayamadım {q}."
                )

    async def my_background_task(self):
        await self.wait_until_ready()

        channel = self.get_channel(DISCORD_CHANNEL_ID)
        print(f"Found channel {channel}.")

        while not self.is_closed():
            await asyncio.sleep(
                (dt.datetime.combine(tomorrow, dt.time.min) - now).seconds
            )

            r = get_rate()

            with open(MENTIONS_FILENAME, "r") as mf:
                mentions = mf.readlines()

            msg = ""

            for i in mentions:
                if msg != "\n":
                    msg += i

            msg += "```"
            msg += f"TRY/USD Oranı: {r}"
            msg += "```"

            await channel.send(msg)
            await self.update_presence()

            now = dt.datetime.now()
            tomorrow = now + dt.timedelta(days=1)


client = MyClient()
client.run(DISCORD_TOKEN)
