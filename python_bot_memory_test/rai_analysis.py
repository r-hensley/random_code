import io

import numpy as np
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from discord.ext import commands
bot = commands.Bot()  # originally for use in an ;eval command, so this line isn't needed, but just to remove errors

channel = bot.get_channel(1318162409420226590)
time = []
memory = []
messages = []
t_offset = 0

async for m in channel.history(limit=100, oldest_first=True):
    s = m.content[1:].split(' ')
    t = int(m.created_at.timestamp())
    if not t_offset:
        t_offset = t
    time.append(t - t_offset)
    m = int(s[0][:-1]) / 1024 ** 2
    memory.append(m)
    messages.append(int(s[1]))

X = np.column_stack((time, messages))  # Combine time and message_count as predictors
y = np.array(memory)  # Memory used as the target

# Create and fit the regression model
model = LinearRegression()
model.fit(X, y)

# Coefficients
a = model.coef_[0]
b = model.coef_[1]
c = model.intercept_

print(f"Memory formula: memory = {a:.2f} * time + {b:.2f} * message_count + {c:.2f}")


def predict_memory(t, m):
    """Predict memory usage for given time (t) and message_count (m)."""
    return a * t + b * m + c


print(predict_memory(60 * 60, 5000))

# Predict values for the input data
y_pred = model.predict(X)

# Calculate residuals (errors)
residuals = y - y_pred

# Print the errors per data point
print("\nErrors per data point:")
print("Index | Actual Memory | Predicted Memory | Error (Residual)")
for i, (actual, predicted, error) in enumerate(zip(y, y_pred, residuals)):
    if i == 25:
        break
    print(f"{i:5} | {actual:13.1f} | {predicted:16.1f} | {error:15.1f}")

print(f"Average residual: {sum(residuals) / len(residuals)}")

# Plot Memory vs Time (fixed message count values shown)
plt.figure(figsize=(8, 6))
plt.scatter(time, memory, color='blue', label='Actual Memory')
plt.scatter(time, y_pred, color='red', label='Predicted Memory')
plt.plot(time, y_pred, color='red', linestyle='--', label='Prediction Line')

plt.xlabel("Time")
plt.ylabel("Memory Used")
plt.title("Memory Used vs Time (with Predictions)")
plt.legend()
plt.grid(True)
image_buffer = io.BytesIO()
plt.savefig(image_buffer, format='png')  # Save the figure as PNG into memory
plt.close()  # Close the figure to free resources
image_buffer.seek(0)  # Move cursor to the start of the buffer

# await ctx.send(file=discord.File(image_buffer, filename="plot.png"))

result = """
Memory formula: memory = 0.06 * time + -0.02 * message_count + 1246.86
1372.2827347195757

Errors per data point:
Index | Actual Memory | Predicted Memory | Error (Residual)
    0 |        1253.7 |           1246.5 |             7.2
    1 |        1253.7 |           1249.7 |             4.0
    2 |        1252.7 |           1252.7 |            -0.0
    3 |        1252.7 |           1255.6 |            -3.0
    4 |        1252.7 |           1258.4 |            -5.8
    5 |        1261.3 |           1261.3 |             0.1
    6 |        1261.3 |           1264.2 |            -2.8
    7 |        1261.3 |           1267.0 |            -5.6
    8 |        1262.9 |           1269.7 |            -6.8
    9 |        1262.9 |           1272.4 |            -9.6
   10 |        1286.3 |           1275.1 |            11.2
   11 |        1287.3 |           1277.9 |             9.5
   12 |        1286.3 |           1280.7 |             5.6
   13 |        1286.3 |           1283.3 |             3.0
   14 |        1286.3 |           1286.0 |             0.4
   15 |        1286.3 |           1288.5 |            -2.2
   16 |        1286.3 |           1291.1 |            -4.8
   17 |        1286.3 |           1293.7 |            -7.4
   18 |        1286.3 |           1296.4 |           -10.1
   19 |        1286.3 |           1299.1 |           -12.8
   20 |        1311.4 |           1301.8 |             9.6
   21 |        1311.4 |           1304.6 |             6.7
   22 |        1311.4 |           1307.1 |             4.2
   23 |        1314.9 |           1309.8 |             5.1
   24 |        1314.0 |           1312.7 |             1.3
Average residual: -8.922258150304042e-14
"""

# note the memory formula is very wrong, it says that more messages means less memory used, which is not true