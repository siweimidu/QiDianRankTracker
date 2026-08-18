"""
榜单注册表 —— 单一事实源。

起点中文网排行榜（https://www.qidian.com/rank/）的全部 16 个榜单类型：
  付费盘：月票 / 畅销 / VIP 收藏 / 更新
  流量盘：阅读指数 / 追读 / 收藏 / 书友 / 推荐 / 留存
  新书盘：签约作者新书 / 公众作者新书 / 新人签约新书 / 新人作者新书
  女生盘：女生精选 / 女生月票

每个榜单的分类目录（玄幻/仙侠/都市…）在抓取时从榜单页的
data-chanid 导航自动发现，无需手工维护。

字段：
  slug    英文短名，决定 data/<slug>/ 与 api/<slug>/
  name    中文榜单名
  path    /rank/<path>/ 的路径段
  channel male / female
  group   前端分组：paid 付费 / traffic 流量 / newbook 新书 / female 女生
  metric  榜单核心指标名（展示用；实际值从页面动态解析）
  enabled 是否参与抓取
"""

BOARDS = [
    # ---- 付费价值盘 ----
    {"slug": "yuepiao",       "name": "月票榜",         "path": "yuepiao",
     "channel": "male", "group": "paid",    "metric": "月票",     "enabled": True},
    {"slug": "hotsales",      "name": "畅销榜",         "path": "hotsales",
     "channel": "male", "group": "paid",    "metric": "畅销指数", "enabled": True},
    {"slug": "vipcollect",    "name": "VIP收藏榜",      "path": "vipcollect",
     "channel": "male", "group": "paid",    "metric": "VIP收藏",  "enabled": True},
    {"slug": "vipup",         "name": "更新榜",         "path": "vipup",
     "channel": "male", "group": "paid",    "metric": "更新",     "enabled": True},
    # ---- 流量热度盘 ----
    {"slug": "readindex",     "name": "阅读指数榜",     "path": "readindex",
     "channel": "male", "group": "traffic", "metric": "阅读指数", "enabled": True},
    {"slug": "followreading", "name": "追读榜",         "path": "followReading",
     "channel": "male", "group": "traffic", "metric": "追读",     "enabled": True},
    {"slug": "collect",       "name": "收藏榜",         "path": "collect",
     "channel": "male", "group": "traffic", "metric": "收藏",     "enabled": True},
    {"slug": "newfans",       "name": "书友榜",         "path": "newfans",
     "channel": "male", "group": "traffic", "metric": "书友",     "enabled": True},
    {"slug": "recom",         "name": "推荐榜",         "path": "recom",
     "channel": "male", "group": "traffic", "metric": "推荐票",   "enabled": True},
    {"slug": "retention",     "name": "留存榜",         "path": "retention",
     "channel": "male", "group": "traffic", "metric": "留存",     "enabled": True},
    # ---- 新书孵化盘 ----
    {"slug": "signnewbook",   "name": "签约作者新书榜", "path": "signnewbook",
     "channel": "male", "group": "newbook", "metric": "月票",     "enabled": True},
    {"slug": "pubnewbook",    "name": "公众作者新书榜", "path": "pubnewbook",
     "channel": "male", "group": "newbook", "metric": "推荐票",   "enabled": True},
    {"slug": "newsign",       "name": "新人签约新书榜", "path": "newsign",
     "channel": "male", "group": "newbook", "metric": "月票",     "enabled": True},
    {"slug": "newauthor",     "name": "新人作者新书榜", "path": "newauthor",
     "channel": "male", "group": "newbook", "metric": "推荐票",   "enabled": True},
    # ---- 女生频道（/rank/mm/<type>/，平铺榜，无分类导航）----
    {"slug": "female-yuepiao",   "name": "女生月票榜", "path": "mm/yuepiao",
     "channel": "female", "group": "female", "metric": "月票",     "enabled": True},
    {"slug": "female-hotsales",  "name": "女生畅销榜", "path": "mm/hotsales",
     "channel": "female", "group": "female", "metric": "畅销指数", "enabled": True},
    {"slug": "female-recom",     "name": "女生推荐榜", "path": "mm/recom",
     "channel": "female", "group": "female", "metric": "推荐票",   "enabled": True},
    {"slug": "female-collect",   "name": "女生收藏榜", "path": "mm/collect",
     "channel": "female", "group": "female", "metric": "收藏",     "enabled": True},
    {"slug": "female-newfans",   "name": "女生书友榜", "path": "mm/newfans",
     "channel": "female", "group": "female", "metric": "书友",     "enabled": True},
    {"slug": "female-readindex", "name": "女生阅读指数榜", "path": "mm/readindex",
     "channel": "female", "group": "female", "metric": "阅读指数", "enabled": True},
    {"slug": "female-newsign",   "name": "女生签约新书榜", "path": "mm/signnewbook",
     "channel": "female", "group": "female", "metric": "月票",     "enabled": True},
]

GROUP_LABELS = {
    "paid": "付费价值盘",
    "traffic": "流量热度盘",
    "newbook": "新书孵化盘",
    "female": "女生频道",
}

# ---- 题材关键词：命中简介/子分类即计入赛道热度 ----
MALE_KEYWORDS = [
    "系统", "重生", "穿越", "无敌", "签到", "苟道", "种田", "无限流", "诸天", "万界",
    "都市", "异能", "兵王", "战神", "赘婿", "神医", "金融", "鉴宝", "直播", "诡异",
    "玄幻", "修仙", "炼丹", "宗门", "废柴", "天才", "废土", "末世", "丧尸", "星际",
    "机甲", "科技", "工业", "国运", "历史", "争霸", "三国", "大明", "网游", "电竞",
    "副本", "克苏鲁", "灵异", "规则怪谈", "悬疑", "推理", "盗墓", "御兽", "聊天群",
    "扮猪吃虎", "杀伐果断", "热血", "经营", "官场", "谍战", "反派", "家族修仙",
]

FEMALE_KEYWORDS = [
    "重生", "穿书", "快穿", "系统", "空间", "团宠", "萌宝", "女配", "炮灰",
    "反派", "权臣", "宅斗", "宫斗", "和离", "替嫁", "逃荒", "种田", "美食", "经商",
    "年代", "七零", "八零", "军婚", "豪门", "总裁", "真假千金", "先婚后爱", "追妻",
    "甜宠", "双洁", "无CP", "末世", "废土", "天灾", "囤货", "异能", "玄学",
    "国运", "星际", "修仙", "无限流", "悬疑", "直播", "综艺", "娱乐圈",
    "校园", "暗恋", "青梅竹马", "民国", "兽世", "基建", "嫡女", "王妃", "女帝",
]

GENERAL_KEYWORDS = list(dict.fromkeys(MALE_KEYWORDS + FEMALE_KEYWORDS))

# 大频道 → 赛道分组（跨分类聚合用）
GENRE_GROUPS = {
    "male": [
        {"name": "玄幻仙侠", "sub": ["东方玄幻", "异世大陆", "王朝争霸", "高武世界",
                                "古典仙侠", "现代修真", "洪荒", "幻想修仙"]},
        {"name": "都市现实", "sub": ["都市生活", "都市异能", "异术超能", "现实百态",
                                "人间百态", "商战职场", "青春文学", "娱乐明星"]},
        {"name": "历史军事", "sub": ["架空历史", "历史传记", "秦汉三国", "两晋隋唐",
                                "外国历史", "军旅生活", "军事战争", "抗战烽火",
                                "谍战特工"]},
        {"name": "科幻无限", "sub": ["超级科技", "进化变异", "时空穿梭", "末世危机",
                                "星际文明", "诸天无限", "衍生同人"]},
        {"name": "悬疑灵异", "sub": ["诡秘悬疑", "奇妙世界", "灵异鬼怪", "探险生存",
                                "侦探推理"]},
        {"name": "游戏竞技", "sub": ["游戏系统", "游戏异界", "电子竞技", "体育赛事",
                                "篮球运动", "足球运动"]},
    ],
    "female": [
        {"name": "古代言情", "sub": ["古代言情", "宫闱宅斗", "经商种田", "西方时空",
                                 "清穿民国", "上古蛮荒"]},
        {"name": "现代言情", "sub": ["现代言情", "豪门总裁", "婚恋情缘", "商战职场",
                                 "青春文学", "娱乐明星"]},
        {"name": "幻想言情", "sub": ["幻想言情", "仙侠奇缘", "玄幻言情", "科幻空间",
                                 "悬疑灵异", "千古芳华"]},
        {"name": "浪漫青春", "sub": ["浪漫青春", "青春纯爱", "青春校园", "叛逆成长"]},
    ],
}


def enabled_boards() -> list:
    return [b for b in BOARDS if b.get("enabled")]


def get_board(slug: str):
    for b in BOARDS:
        if b["slug"] == slug:
            return b
    return None


def board_public_meta(board: dict) -> dict:
    return {
        "slug": board["slug"],
        "name": board["name"],
        "channel": board["channel"],
        "group": board.get("group", ""),
        "group_label": GROUP_LABELS.get(board.get("group", ""), ""),
        "metric": board.get("metric", ""),
    }
