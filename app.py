# -*- coding: utf-8 -*-
import multiprocessing
import time
import datetime
from frame.log_helper import LogHelper
from frame import config, metric_helper
from service.qcloud_query import QcloudQuery
import signal

logger = LogHelper().logger


def func(*args):
    load_balancer_vips = args[0]
    load_balancer_name = args[1]
    cur_time = args[2]
    # 负载均衡实例的网络类型
    # 2：公网属性， 3：内网属性。
    load_balancer_type = args[3]
    vpc_id = args[4]

    metric_list = ["connum", "new_conn", "intraffic", "outtraffic"]
    qcloud_query = QcloudQuery()
    metrics = []
    endpoint = str(load_balancer_name)
    action_params = {
        "namespace": "qce/lb_public",
        "dimensions.0.name": "vip",
        "period": 60,
        "dimensions.0.value": load_balancer_vips,
        "metricName": "",
        "startTime": cur_time,
        "endTime": cur_time
    }
    # 负载均衡内网服务器维度
    if load_balancer_type == 3 or load_balancer_type == "3":
        action_params["namespace"] = "qce/lb_private"
        action_params["dimensions.1.name"] = "vpcId"
        action_params["dimensions.1.value"] = vpc_id

    for metric in metric_list:
        logger.info('开始获取负载均衡监控: %s 监控信息。metric: %s ', str(load_balancer_name),
                    metric)
        try:
            action_params["metricName"] = metric
            result = qcloud_query.get_monitor("sh", action_params)
            val = None
            if result and result.get("code") == 0 and result.get("dataPoints"):
                val = result.get("dataPoints")[0]
            else:
                logger.error('获取负载均衡监控: %s .metric信息: %s .监控信息获取失败',
                             str(load_balancer_name), metric)
            m = metric_helper.gauge_metric(endpoint, metric, val)
            m["step"] = config.INTERVAL
            m['timestamp'] = int(
                time.mktime(time.strptime(cur_time, '%Y-%m-%d %H:%M:%S')))
            metrics.append(m)
        except Exception:
            logger.exception('获取负载均衡监控: %s .metric信息: %s .监控信息出现异常。',
                             str(load_balancer_name), metric)
    if metrics:
        metric_helper.push_metrics(metrics)
    logger.info('结束获取负载均衡监控: %s 监控信息', str(load_balancer_name))


if __name__ == "__main__":
    today = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
    logger.info('=====%s负载监控开始运行=====', today)
    process_count = (multiprocessing.cpu_count() * 2 +
                     1) if (multiprocessing.cpu_count() * 2 + 1) < 11 else 10
    logger.info('程序启动，进程数%s', process_count)
    while True:
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(process_count)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            dt = datetime.datetime.now() + datetime.timedelta(minutes=-3)
            cur_time = dt.strftime('%Y-%m-%d  %H:%M:00')

            # 查询一条取出total
            qcloud_query = QcloudQuery()
            lb_result = qcloud_query.get_lb_list("sh", {
                "limit": 1,
                "forward": -1
            })
            # 获取所有的负载均衡
            all_lb_result = qcloud_query.get_lb_list(
                "sh", {
                    "limit": lb_result.get("totalCount"),
                    "forward": -1
                })
            lb_list = all_lb_result.get("loadBalancerSet")
            logger.info('当前负载均衡设备数:%s', len(lb_list))
            for lb in lb_list:
                load_balancer_vips = lb.get("loadBalancerVips")[0]
                load_balancer_name = lb.get("loadBalancerName")
                load_balancer_type = lb.get("loadBalancerType")
                vpc_id = lb.get("vpcId")
                pool.apply_async(func, (load_balancer_vips, load_balancer_name,
                                        cur_time, load_balancer_type, vpc_id))

            pool.close()
            pool.join()

            today = time.strftime('%Y-%m-%d  %H:%M:%S',
                                  time.localtime(time.time()))
            logger.info('=====%s所有负载监控获取完成=====', today)
        except KeyboardInterrupt:
            logger.error("Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
        except Exception:
            logger.exception('程序出现异常。')

        time.sleep(config.INTERVAL)
