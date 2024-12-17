# This is going to be a basic bot which will be used to test the memory usage of the bot.
# Specifically, the message cache and how much a larger max_messages setting will affect the bot.
# Start a tracemalloc session at the very beginning, and then output the memory usage as the message_cache fills.

import tracemalloc
tracemalloc.start()

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(f'{dir_path}/.env')

# tracemalloc.get_traced_memory()
# Get the current size and peak size of memory blocks traced by the tracemalloc module as a tuple: (current: int, peak: int).

# tracemalloc.get_tracemalloc_memory()
# Get the memory usage in bytes of the tracemalloc module used to store traces of memory blocks. Return an int.

# tracemalloc.take_snapshot()
# Take a snapshot of traces of memory blocks allocated by Python. Return a new Snapshot instance.
#
# The snapshot does not include memory blocks allocated before the tracemalloc module started to trace memory allocations.
#
# Tracebacks of traces are limited to get_traceback_limit() frames. Use the nframe parameter of the start() function to store more frames.
#
# The tracemalloc module must be tracing memory allocations to take a snapshot, see the start() function.
#
# See also the get_object_traceback() function.



# SNAPSHOT (10 files allocating most memory)
# snapshot = tracemalloc.take_snapshot()
# top_stats = snapshot.statistics('lineno')
#
# print("[ Top 10 ]")
# for stat in top_stats[:10]:
#     print(stat)
#
# (traceback of largest file)
# top_stats = snapshot.statistics('traceback')
#
# # pick the biggest memory block
# stat = top_stats[0]
# print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
# for line in stat.traceback.format():
#     print(line)


# COMPARING SNAPSHOTS
# snapshot1 = tracemalloc.take_snapshot()
# # ... call the function leaking memory ...
# snapshot2 = tracemalloc.take_snapshot()
#
# top_stats = snapshot2.compare_to(snapshot1, 'lineno')
#
# print("[ Top 10 differences ]")
# for stat in top_stats[:10]:
#     print(stat)

# CURRENT TOTAL MEMORY
# size, peak = tracemalloc.get_traced_memory()
# print(f"{size=}, {peak=}")

snapshots: list[tuple[tracemalloc.Snapshot, int, float, str]] = []

def filter_snapshot(snapshot: tracemalloc.Snapshot) -> tracemalloc.Snapshot:
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
        tracemalloc.Filter(False, "C:\\Users\\ryry0\\AppData\\Local\\Programs\\Python\\Python310\\lib\\tracemalloc.py"),
        tracemalloc.Filter(True, "*state.py"),
        tracemalloc.Filter(True, "*message.py"),
    
    ))
    return snapshot


def display_detailed_allocations(snapshot: tracemalloc.Snapshot, file_filter: str, line_filter: int):
    """Display detailed memory allocations for a specific file and line."""
    # Filter snapshot for a specific file and line
    file_filter = file_filter.replace("/", "\\")
    filtered_traces = snapshot.filter_traces((
        tracemalloc.Filter(True, "*" + file_filter),
    ))
    
    print(f"Memory allocations for {file_filter} (line {line_filter}):")
    
    for trace in reversed(filtered_traces.traces):
        traceback = trace.traceback
        for frame in traceback:
            if frame.filename.endswith(file_filter) and frame.lineno == line_filter:
                print(f"Allocation: {trace.size:.1f} B")
                # print(f"Traceback (most recent call last):")
                # for frame2 in traceback:
                #     print(f"  File: {frame2.filename}, Line: {frame2.lineno}")
                # print()
    
    # # Find memory traces for the specific line
    # for stat in filtered_traces.statistics("traceback"):
    #     # print(f"Searching: {stat}")
    #     for frame in stat.traceback:
    #         # print(f"Frame: {frame}, {frame.filename}, {frame.lineno}", file_filter, frame.filename.endswith(file_filter), line_filter, frame.lineno == line_filter)
    #         if frame.filename.endswith(file_filter) and frame.lineno == line_filter:
    #             print(f"Allocation: {stat.size / 1024:.2f} KiB")
    #             print(f"Traceback:")
    #             for frame2 in stat.traceback:
    #                 print(f"  File: {frame2.filename}, Line: {frame2.lineno}")

def take_snapshot(description: str = ""):
    s = tracemalloc.take_snapshot()
    s = (s, int(datetime.now().timestamp()), round(get_snapshot_size(s)/1024, 2), description)
    snapshots.append(s)
    
    
    # print snapshot compare_to result with last snapshot
    if len(snapshots) > 1:
        # get two filtered screenshots:
        filtered_one = filter_snapshot(snapshots[-1][0])
        filtered_two = filter_snapshot(snapshots[-2][0])
        
        top_stats = filtered_one.compare_to(filtered_two, 'lineno')
        print_differences = True
        if print_differences:
            print("[ Top 20 differences ]")
            for stat in top_stats[:20]:
                if not stat.count_diff and not stat.size_diff:
                    continue
                stat = str(stat).replace("C:\\Users\\ryry0\\AppData\\Local\\Programs\\Python\\Python310\\lib\\site-packages",
                                         "..")
                stat = str(stat).replace("C:\\Users\\ryry0\\AppData\\Local\\Programs\\Python\\Python310\\lib", "..")
                stat = str(stat).replace("C:\\Users\\ryry0\\Documents\\Python\\random_code", "..")
                stat = str(stat).split(": ")
                print(f"{stat[0]:40}: {stat[1]}")
            
    print(f"\nstate.py traceback stacks:")
    display_detailed_allocations(snapshots[-1][0],
                                 "discord/state.py",
                                 612)

    print(f"{s[2]} KiB - {s[3]}\n\n")

    
    
def get_snapshot_size(snapshot: tracemalloc.Snapshot) -> float:
    return sum(stat.size for stat in snapshot.statistics('lineno'))

take_snapshot("Before defining bot")

# define bot object
max_messages = 5000
class MemoryBot(commands.Bot):
    def __init__(self):
        super().__init__(description="Memory Bot by Ryry013", command_prefix='m.',
                         intents=intents, max_messages=max_messages)
        take_snapshot("Bot is defined")
        
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        take_snapshot("Bot is ready")
        
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)
        
        cache_length = len(self.cached_messages)
        filtered_one = filter_snapshot(snapshots[-1][0])
        filtered_two = filter_snapshot(snapshots[-2][0])
        # mem_diff = round(snapshots[-1][2] - snapshots[-2][2], 1)
        mem_diff = round(get_snapshot_size(filtered_one) - get_snapshot_size(filtered_two) , 1)
        to_send_str = (f"Message processed (len: {len(message.content)}): {cache_length}/{max_messages} "
                       f"- Memory difference: ")
        if mem_diff > 0:
            to_send_str += f"+{mem_diff} KiB"
        else:
            to_send_str += f"{mem_diff} KiB"
        take_snapshot(to_send_str)

def run_bot():
    bot = MemoryBot()
    take_snapshot("Bot instance created")

    key = os.getenv("TOKEN")
    bot.run(key)
    take_snapshot("Bot has been ran")


if __name__ == '__main__':
    run_bot()
