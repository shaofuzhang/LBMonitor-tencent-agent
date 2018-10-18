# -*- coding: utf-8 -*-

from frame.config import secretId, secretKey
from QcloudApi.qcloudapi import QcloudApi
from frame.log_helper import LogHelper
import json

logger = LogHelper().logger


class QcloudQuery(object):
    def __init__(self):
        self.config = {
            'Region': '',
            'secretId': secretId,
            'secretKey': secretKey,
            'method': 'POST',
            'SignatureMethod': 'HmacSHA1',
            'Version': '2017-03-12'
        }

    def get_lb_list(self, region, action_params):
        self.config["Region"] = region
        self.action_params = action_params
        module = "lb"
        action = "DescribeLoadBalancers"
        try:
            service = QcloudApi(module, self.config)
            result = json.loads(service.call(action, self.action_params))
            # logger.info(result)
            if result.get("code") == 0:
                return result
            logger.error("查询负载均衡失败。错误信息:" +
                         result.get("message").encode("utf-8"))
        except Exception:
            logger.exception("查询负载均衡出现异常。")

    def get_monitor(self, region, action_params):
        self.config["Region"] = region
        self.action_params = action_params
        module = "monitor"
        action = "GetMonitorData"
        try:
            service = QcloudApi(module, self.config)
            print(service.generateUrl(action, self.action_params))
            result = json.loads(service.call(action, self.action_params))
            logger.info(result)
            if result.get("code") == 0:
                return result
            logger.error("查询监控信息失败。错误信息:" +
                         result.get("message").encode("utf-8"))
        except Exception:
            logger.exception("查询监控信息出现异常。")
