# 腾讯云负载均衡采集器

## 采集范围

腾讯云下所有的负载均衡设备，**负载均衡维度**的指标。

采集指标:

| 指标名称（metricName) | 含义       | 单位 |
| --------------------- | ---------- | ---- |
| connum                | 当前连接数 | 个   |
| new_conn              | 新增连接数 | 个   |
| intraffic             | 入流量     | Mbps |
| outtraffic            | 出流量     | Mbps |


## 运行环境

Pyhton2.7.12+

## 运行

1. 在frame/config.py 增加

``` python
secretId = 'your secretId'
secretKey = 'your secretKey'
```

2. 安装Python依赖

```shell
pip install -r requirements.txt
```

3. 运行

```shell
python app.py
```

