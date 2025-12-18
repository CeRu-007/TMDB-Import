import json
from urllib.parse import urlparse
import logging
from ..common import Episode, open_url
from datetime import datetime

# language: zh-CN
# backdrop: 860*484
# Ex:"https://www.viu.com/ott/sg/zh-cn/vod/309897/"

# 区域映射表
AREA_ID_MAP = {
    'sg': 2,    # 新加坡
    'hk': 1,    # 香港
}

# 语言映射表
LANGUAGE_FLAG_ID_MAP = {
    'zh-cn': 2,  # 简体中文
    'zh': 1,  # 繁体中文(香港)
}

def viu_extractor(url):
    logging.info("viu_extractor is called")
    
    urlData = urlparse(url)
    urlPath = urlData.path.strip('/')
    
    # 解析 URL 路径: ott/{area}/{language}/vod/{product_id}
    path_parts = urlPath.split('/')
    if len(path_parts) >= 4:
        area_code = path_parts[1]  # sg
        language_code = path_parts[2]  # zh-cn
        product_id = path_parts[4]
    else:
        # 如果解析失败,使用默认值
        area_code = 'sg'
        language_code = 'zh-cn'
        product_id = urlPath.rsplit('/', 1)[-1]
    
    # 获取对应的 ID
    area_id = AREA_ID_MAP.get(area_code.lower(), 2)  # 默认值 2 (新加坡)
    language_flag_id = LANGUAGE_FLAG_ID_MAP.get(language_code.lower(), 2)  # 默认值 2 (简体中文)
    
    logging.debug(f"Parsed area_code: {area_code}, area_id: {area_id}")
    logging.debug(f"Parsed language_code: {language_code}, language_flag_id: {language_flag_id}")
    
    apiRequest = f"https://www.viu.com/ott/{area_code}/index.php?area_id={area_id}&language_flag_id={language_flag_id}&r=vod/ajax-detail&platform_flag_label=web&product_id={product_id}"
    logging.debug(f"API request url: {apiRequest}")
    soureData = json.loads(open_url(apiRequest))
    series = soureData["data"]["series"]
    season_number = 1
    season_name = series["name"]
    season_overview = series["description"]
    
    episodes = {}
    for episode in series["product"][::-1]:
        apiRequest = f"https://www.viu.com/ott/{area_code}/index.php?area_id={area_id}&language_flag_id={language_flag_id}&r=vod/ajax-detail&platform_flag_label=web&product_id={episode['product_id']}"
        logging.debug(f"API request url: {apiRequest}")
        soureData = json.loads(open_url(apiRequest))
        current_product = soureData["data"]["current_product"]
        episode_number = current_product["number"]
        episode_name = current_product["synopsis"]
        episode_air_date = datetime.fromtimestamp(int(current_product["schedule_start_time"])).date()
        episode_runtime = round(int(current_product["time_duration"])/60)
        episode_overview = current_product["description"]
        episode_backdrop = current_product["cover_image_url"]
        episodes[episode_number] = Episode(episode_number, episode_name, episode_air_date, episode_runtime, episode_overview, episode_backdrop)
    return episodes