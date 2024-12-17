# Python Bot Memory Test

This was a silly project I made to test the memory usage of a Python bot. The bot is designed to measure and report memory usage as it processes messages, specifically focusing on the message cache and the impact of different `max_messages` settings.

## Features

- Tracks memory usage using `tracemalloc`.
- Reports memory differences after processing messages.
- Provides detailed memory allocation statistics.

## Files

- `bot.py`: Main bot implementation and memory tracking logic.
- `message.py`: Contains message handling and editing functions.
- `result.txt`: Sample output of memory usage statistics.


## Usage

The bot will log memory usage statistics to the console as it processes messages.

The `result.txt` file shows detailed memory usage statistics for the bot as it processes messages. The memory usage is tracked using `tracemalloc`, and snapshots are taken at various stages of the bot's lifecycle. The file includes memory allocation details for specific lines in the `discord` library, particularly focusing on `state.py` and `message.py`.

To determine how much memory one message takes up in the memory cache, you can look at the memory difference reported after processing each message.

It seems the message object itself takes up 320B per message. Total memory added per message looks to be around 1000KB.

That's a bit more than I expected, as when I [tested it with Rai](rai_result.txt) and 5000 messages, it started at 1253.6MB of memory and ended at 1462.9MB of memory. That's a difference of 209.3MB for 5000 messages, or about 41.86KB per message. But anyway, I learned some about tracemalloc...

I also tried applying a linear regression to the Rai result, but it gave a nonsensical answer as it said the memory had a negative dependence on message count. See [rai_analysis.py](rai_analysis.py) for the code.

