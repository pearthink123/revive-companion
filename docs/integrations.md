# Integrations

## Telegram Bot

```python
from revive_companion import CompanionEngine
import telegram

engine = CompanionEngine(config="default")
bot = telegram.Bot(token="YOUR_TOKEN")
chat_id = "YOUR_CHAT_ID"

while True:
    result = engine.decide()
    if result.should_send:
        await bot.send_message(chat_id=chat_id, text=result.response)
        engine.record_send()

    # When user replies
    engine.record_reply(message="...", reply_speed=0.8, reply_length=0.5)
```

## Discord Bot

```python
import discord
from revive_companion import CompanionEngine

engine = CompanionEngine(config="default")
client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    while True:
        result = engine.decide()
        if result.should_send:
            await channel.send(result.response)
            engine.record_send()
        await asyncio.sleep(30 * 60)  # 30 min

@client.event
async def on_message(message):
    if message.author != client.user:
        engine.record_reply(
            message=message.content,
            reply_speed=0.8,
            reply_length=len(message.content) / 100,
        )
```

## With affective-longing

For deeper emotional modeling, combine with [affective-longing](https://github.com/pearthink123/affective-longing):

```python
from revive_companion import PoissonLove
from affective_longing import AffectiveLonging

love = PoissonLove()
longing = AffectiveLonging()

# Each tick
result = love.tick()
if result.should_send:
    # Check emotional state before sending
    state = longing.get_state()
    if state["emotion"]["valence"] > 0.3:
        send_message(longing.compose_message())
        love.record_send()
        longing.remember("sent caring message", emotional_weight=0.7)
```

## Custom Adapter

```python
from revive_companion.adapters.base import Adapter

class MyAdapter(Adapter):
    def send(self, system_prompt, user_prompt):
        # Your LLM call here
        return my_llm_call(system_prompt, user_prompt)

engine = CompanionEngine(adapter=MyAdapter(config))
```
