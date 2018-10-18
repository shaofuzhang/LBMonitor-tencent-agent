import random
import requests
from frame.log_helper import LogHelper
from frame.config import TRANSFER, INTERVAL

logger = LogHelper().logger


# metric
def make_metric(endpoint, metric, value, datatype, **tags):
    if tags:
        tags = ["{0}={1!s}".format(k, v) for k, v in tags.items()]
        tags = ",".join(tags)
    else:
        tags = ""
    return {
        "endpoint": endpoint,
        "metric": metric,
        "tags": tags,
        "value": value,
        "counterType": datatype,
    }


def gauge_metric(endpoint, metric, value, **tags):
    return make_metric(endpoint, metric, value, "GAUGE", **tags)


def counter_metric(endpoint, metric, value, **tags):
    return make_metric(endpoint, metric, value, "COUNTER", **tags)


def push_metrics(metrics):
    logger.info(metrics)
    transfers = TRANSFER
    for i in range(len(transfers)):
        try:
            addr = random.choice(transfers)
            r = requests.post(
                "http://%s/api/push" % addr,
                json=metrics,
                timeout=INTERVAL * 0.6)
            logger.info(r.text)
            if r.ok:
                break
        except Exception, e:
            transfers.remove(addr)
            logger.info("push %d  metrics failed: %s" % (len(metrics), str(e)))