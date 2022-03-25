import copy
import json
from decimal import Decimal
from typing import Dict, Union

from .logger import Logger


def format_data(data: Dict):
    try:
        data = empty2null(data)
        data = json.loads(json.dumps(data), parse_float=Decimal)
    except Exception as e:
        Logger.e('format_data', f'Failed to format data : {e}')

    return data


def empty2null(data: Dict) -> Union[Dict, None]:
    """[summary]

    Args:
        data (Dict): [description]

    Returns:
        [type]: [description]
    """
    ret = copy.deepcopy(data)

    if isinstance(data, dict):
        for k, v in ret.items():
            ret[k] = empty2null(v)

    # convert empty string to null
    if data == '':
        ret = None

    return ret
