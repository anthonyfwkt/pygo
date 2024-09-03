import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, LSTM
 
# 导入数据
data = pd.read_csv('data.csv')
# 数据预处理
data['red1'] = (data['red1'] - 1) / 33
data['red2'] = (data['red2'] - 1) / 33
data['red3'] = (data['red3'] - 1) / 33
data['red4'] = (data['red4'] - 1) / 33
data['red5'] = (data['red5'] - 1) / 33
data['red6'] = (data['red6'] - 1) / 33
data['blue'] = (data['blue'] - 1) / 16
# 将数据划分为训练集和测试集
train_data = data.iloc[:1500, :]
test_data = data.iloc[1500:, :]
# 定义函数来生成训练和测试数据
def generate_data(data, lookback):
    X, Y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i+lookback, :])
        Y.append(data[i+lookback, :])
    return np.array(X), np.array(Y)
# 设置LSTM模型参数
lookback = 10
batch_size = 32
epochs = 200
# 生成训练和测试数据
train_X, train_Y = generate_data(train_data[['red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'blue']].values, lookback)
test_X, test_Y = generate_data(test_data[['red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'blue']].values, lookback)
# 创建LSTM模型
model = Sequential()
model.add(LSTM(64, input_shape=(lookback, 7)))
model.add(Dense(32, activation='relu'))
model.add(Dense(7, activation='sigmoid'))
model.compile(loss='mean_squared_error', optimizer='adam')
# 训练模型
model.fit(train_X, train_Y, batch_size=batch_size, epochs=epochs, validation_data=(test_X, test_Y))
# 预测下一期双色球
last_data = data[['red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'blue']].tail(lookback)
last_data = (last_data - 1) / np.array([33, 33, 33, 33, 33, 33, 16])
last_data = np.array(last_data)
last_data = np.reshape(last_data, (1, lookback, 7))
prediction = model.predict(last_data)
prediction = np.round(prediction * np.array([33, 33, 33, 33, 33, 33, 16]) + np.array([1, 1, 1, 1, 1, 1, 1]))
print("下一期双色球预测结果为：", prediction)