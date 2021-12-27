import pandas as pd

frame_test = pd.DataFrame({1999: [74, 38, 39], 2000: [34, 32, 32], 2001: [23, 29, 23]})

print(frame_test)

frame_test2 = pd.DataFrame(
    [[74, 38, 39], [34, 32, 32], [23, 29, 23]], columns=[1999, 2000, 2001]
)

print(frame_test2)
