#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""书签分类规则：按「应用类型」归类。匹配顺序 = 域名 → 关键词 → 原文件夹 → 其他。"""

CATEGORIES = {
    "common":    ("常用（按点击次数）", "fas fa-star"),
    "recent":    ("最近访问", "fas fa-clock"),
    "ecom":      ("电商与店铺后台", "fas fa-store"),
    "ai":        ("AI 与模型平台", "fas fa-robot"),
    "content":   ("内容创作与发布", "fas fa-video"),
    "design":    ("设计与素材", "fas fa-palette"),
    "dev":       ("开发与代码", "fas fa-code"),
    "research":  ("数据与运营分析", "fas fa-chart-bar"),
    "biz":       ("创业与副业", "fas fa-rocket"),
    "freelance": ("接单与外包", "fas fa-handshake"),
    "office":    ("办公与效率工具", "fas fa-briefcase"),
    "learn":     ("学习与课程", "fas fa-graduation-cap"),
    "read":      ("阅读清单", "fas fa-book-open"),
    "net":       ("网络与加速", "fas fa-network-wired"),
    "selfhost":  ("自建与内网服务", "fas fa-server"),
    "social":    ("社交与通讯", "fas fa-comments"),
    "fun":       ("娱乐与游戏", "fas fa-gamepad"),
    "private":   ("私密收藏（勿公开）", "fas fa-lock"),
    "other":     ("其他收藏", "fas fa-globe"),
}

# ---------------- 域名片段（子串匹配，越具体越靠前） ----------------
DOMAIN_RULES = [
    # 电商
    ("ecom", ["myseller.taobao", "item.upload.taobao", "upload.taobao", "qn.taobao", "waybill.wuliu",
              "taobao.com", "tmall.com", "pinduoduo", "yangkeduo", "jinritemai", "xiaohongshu",
              "tiktokshop", "seller-my.tiktok", "seller.tiktok", "shopee", "lazada", "aliexpress",
              "1688.com", "alibaba.com", "alimama", "taobao", "jd.com", "youzan", "weidian",
              "91miaoshou", "chengji-inc", "goofish", "xianyu", "douchacha", "chanmama", "feigua",
              "kuaishou", "douyin.com/", "pipopay"]),
    # AI
    ("ai", ["openai", "chatgpt", "claude.ai", "anthropic", "gemini.google", "aistudio", "deepseek",
            "toapis", "302.ai", "302ai", "openrouter", "huggingface", "replicate.com", "midjourney",
            "leonardo.ai", "lexica.art", "comfy", "stability.ai", "runwayml", "pika.art", "kling",
            "hailuo", "minimax", "volcengine", "volc.ai", "qwen", "dashscope", "moonshot", "kimi",
            "zhipu", "bigmodel", "cohere", "groq.com", "together.ai", "fireworks.ai", "ollama",
            "colab.research.google", "notebooklm", "cursor.com", "codebuddy", "manus.im", "tripo",
            "meshy", "elevenlabs", "suno.com", "udio", "heygen", "synthesia", "sora", "civitai",
            "openart", "fal.ai", "novita", "siliconflow", "imcp.pro", "mcp.so", "smithery",
            "pulsemcp", "tokenrize", "perplexity", "poe.com", "character.ai", "mistral", "x.ai",
            "grok.com", "jasper", "copy.ai", "writesonic", "gamma.app", "notion.ai", "gpt-", "llm",
            "agent", "flowith", "coze", "dify", "n8n.io", "make.com", "zapier"]),
    # 设计
    ("design", ["figma", "dribbble", "behance", "huaban", "pinterest", "pexels", "pixabay", "unsplash",
                "freepik", "iconfont", "icons8", "worldvectorlogo", "flaticon", "lottiefiles", "canva",
                "designkit", "remove.bg", "photopea", "sketch.com", "adobe", "coolors", "zcool",
                "undraw", "storyset", "drawkit", "dafont", "fonts.google", "zhimg", "cults3d",
                "thingiverse", "printables", "myfonts", "ui8", "envato", "elements.envato", "istock",
                "shutterstock", "gettyimages", "vecteezy", "cleanpng", "pngtree"]),
    # 开发
    ("dev", ["github.com", "gitlab", "gitee.com", "bitbucket", "stackoverflow", "npmjs", "pypi",
             "hub.docker", "docker.com", "vercel", "netlify", "cloudflare", "heroku", "railway.app",
             "render.com", "developer.", "docs.", "mdn.", "dev.to", "juejin", "csdn", "segmentfault",
             "v2ex", "rsshub", "postman", "regex101", "sqlite", "python.org", "nodejs.org", "go.dev",
             "rust-lang", "php.net", "laravel", "djangoproject", "nextjs", "reactjs", "react.dev",
             "vuejs", "tailwindcss", "npm", "cdn.jsdelivr", "unpkg", "jsdelivr", "codepen",
             "codesandbox", "stackblitz", "sourcegraph", "npmtrends", "caniuse", "json.cn", "bejson",
             "openwrt.org", "kernel.org", "nginx", "apache.org", "mozilla", "chromium",
             "chromewebstore", "addons.mozilla", "web.archive"]),
    # 数据与运营分析
    ("research", ["trends.google", "semrush", "ahrefs", "similarweb", "socialblade", "statista",
                  "gartner", "forrester", "iresearch", "questmobile", "trendinsight", "index.baidu",
                  "tophub", "newrank", "新榜", "datawrapper", "kaggle", "ourworldindata", "stat.gov",
                  "36kr", "huxiu", "qbitai", "量子位", "geekpark", "cyzone", "itjuzi"]),
    # 创业与副业
    ("biz", ["indiehackers", "producthunt", "stripe.com", "gumroad", "lemonsqueezy", "paddle",
             "partnerstack", "impact.com", "cj.com", "awin", "clickbank", "digistore24", "teespring",
             "printful", "shopify", "waimaomike", "amz123", "sellics", "helium10", "junglescout"]),
    # 接单与外包
    ("freelance", ["upwork", "fiverr", "freelancer.com", "toptal", "zbj.com", "epwk", "680.com",
                   "vikecn", "sxsoft", "proginn", "codemart", "51cxy", "yuanjisong", "waibaodaren"]),
    # 办公与效率
    ("office", ["notion", "feishu", "larksuite", "lark.", "gmail", "mail.google", "drive.google",
                "docs.google", "sheets.google", "calendar.google", "office.com", "wps", "airtable",
                "trello", "miro.com", "diagrams.net", "processon", "cli.im", "convertio", "ilovepdf",
                "smallpdf", "wetransfer", "zion.", "mubu", "xmind", "yuque", "teambition", "dingtalk",
                "wecom", "baidu.com/s?", "pan.baidu", "aliyundrive", "115.com", "jianguoyun",
                "weather.com", "qweather", "translate.google", "deepl", "grammarly", "quillbot"]),
    # 学习
    ("learn", ["coursera", "udemy", "udacity", "edx.org", "khanacademy", "arxiv", "scholar.google",
               "wikipedia", "zhihu.com", "imooc", "jikexueyuan", "runoob", "w3school", "liaoxuefeng",
               "deeplearning.ai", "fast.ai", "openreview", "paperswithcode", "semanticscholar",
               "bilibili.com/video", "xuetangx", "icourse163", "duolingo", "youdao", "iciba"]),
    # 阅读
    ("read", ["medium.com", "substack", "readwise", "instapaper", "getpocket", "feedly", "inoreader",
              "weread.qq", "dedao", "docin", "wenku.baidu", "360doc", "jiemian", "thepaper",
              "newsletter", "mirror.xyz", "sspai.com", "ruanyifeng", "coolshell", "book.douban",
              "douban.com"]),
    # 网络与加速
    ("net", ["cshjc", "bncrcloud", "valtrogen", "berrypass", "realiti.me", "jichang", "ytoo",
             "justmysocks", "v2ray", "clash", "shadowrocket", "dnschecker", "ip.sb", "ipinfo",
             "ping.", "itdog", "boce", "17ce", "站长工具", "chinaz", "aizhan"]),
    # 自建与内网
    ("selfhost", ["synology", "quickconnect", "openwrt", "luci", "alist", "aria2", "phpmyadmin",
                  "frps", "frp.", "nps.", "esxi", "proxmox", "piwigo", "home-assistant", "hass.io",
                  "typecho", "joomla", "migpt", "lighthouse", "宝塔", "bt.cn", "portainer",
                  "grafana", "prometheus", "vaultwarden", "nextcloud", "immich", "jellyfin",
                  "emby", "transmission", "qbit", "nas.", "unraid", "ikuai", "mikrotik"]),
    # 社交
    ("social", ["x.com", "twitter.com", "facebook.com", "instagram.com", "t.me", "telegram",
                "discord", "weibo.com", "linkedin.com", "reddit.com", "threads.net", "whatsapp",
                "wechat.com", "qq.com", "douban.com/people"]),
    # 娱乐
    ("fun", ["steam", "playhop", "netflix", "spotify", "music.163", "y.qq.com", "iqiyi", "youku",
             "mgtv", "douban.com/movie", "twitch", "epicgames", "itch.io", "hoyolab", "bilibili.com",
             "youtube.com", "youtu.be", "poki", "4399", "7k7k"]),
    # 内容创作（放最后，避免吃掉 bilibili/youtube 之外的判断）
    ("content", ["mp.weixin", "mp.toutiao", "toutiao.com", "douyin.com", "tiktok.com", "patreon",
                 "socialecho", "obs", "capcut", "jianying", "剪映", "新片场", "xinpianchang",
                 "chuangkit", "创客贴", "editor.", "studio.youtube", "creator.", "weixin.qq"]),
]

# ---------------- 关键词（站点名 / 原文件夹名） ----------------
WORD_RULES = [
    ("selfhost", ["群晖", "威联通", "路由器", "软路由", "内网", "自建", "nas", "服务器", "面板",
                  "控制台", "docker", "容器", "图床", "图库", "网盘", "备份"]),
    ("ecom", ["电商", "店铺", "商家", "卖家", "订单", "商品", "上货", "打单", "选品", "跨境",
              "抖店", "千牛", "小店", "直播带货", "联盟营销", "affiliate", "dropship", "独立站"]),
    ("ai", ["ai", "人工智能", "大模型", "模型", "gpt", "提示词", "prompt", "生成", "智能体", "agent",
            "语音克隆", "换脸", "配音", "tss", "tts", "画图", "文生图", "文生视频"]),
    ("content", ["自媒体", "公众号", "头条", "视频", "直播", "剪辑", "字幕", "短视频", "素材站",
                 "新媒体", "选题", "爆款"]),
    ("design", ["设计", "素材", "图片", "图标", "字体", "配色", "海报", "模板", "logo", "svg",
                "png", "壁纸", "3d", "建模", "渲染"]),
    ("dev", ["开发", "代码", "编程", "文档", "api", "教程", "github", "开源", "脚本", "vps",
             "建站", "wordpress", "主题", "插件", "sdk"]),
    ("research", ["数据", "指数", "趋势", "分析", "排行", "榜单", "报告", "研报", "热榜", "监测",
                  "洞察", "行业", "咨询", "统计"]),
    ("biz", ["创业", "副业", "项目", "变现", "出海", "选品", "商业模式", "独立开发", "接单",
             "赚钱", "流量", "私域"]),
    ("freelance", ["威客", "外包", "众包", "接单", "兼职", "任务平台"]),
    ("office", ["办公", "文档", "表格", "表单", "转换", "pdf", "工具", "效率", "二维码", "笔记",
                "日历", "待办", "会议", "协作"]),
    ("learn", ["学习", "课程", "教程", "教案", "考试", "论文", "百科", "公开课", "训练营", "知识"]),
    ("read", ["阅读", "书单", "读书", "文章", "博客", "资讯", "新闻", "周刊", "稍后读", "订阅",
              "付费阅读", "arc", "reading", "rss"]),
    ("net", ["翻墙", "机场", "加速", "代理", "梯子", "订阅", "vpn", "节点", "测速", "dns"]),
    ("social", ["社交", "微博", "微信", "朋友圈", "社群", "论坛", "社区"]),
    ("fun", ["游戏", "影视", "音乐", "娱乐", "追剧", "动漫", "电影"]),
]

# ---------------- 原文件夹兜底（当域名和关键词都没命中） ----------------
FOLDER_RULES = [
    ("read", ["arc / reading", "reading", "付费阅读", "稍后读", "书签备份"]),
    ("selfhost", ["家", "翻墙路由", "服务器"]),
    ("research", ["咨询、趋势", "数据分析", "运营"]),
    ("freelance", ["威客"]),
    ("biz", ["创业项目", "创业"]),
    ("ecom", ["电商", "tt"]),
    ("net", ["翻墙"]),
    ("learn", ["教案", "学习", "课程"]),
    ("design", ["设计", "素材"]),
    ("office", ["工具类", "工具"]),
    ("dev", ["开发", "技术", "代码"]),
    ("content", ["自媒体"]),
]

PRIVATE_HOST_HINTS = ("synology", "quickconnect", "openwrt", "luci", "alist", "aria2", "phpmyadmin",
                      "frps", "esxi", "piwigo", "home-assistant", "typecho", "joomla", "migpt",
                      "lighthouse", "portainer", "nextcloud", "immich", "jellyfin", "emby", "nps")


def classify(host, text, folders=()):
    h = host.lower()
    for cat, frags in DOMAIN_RULES:
        if any(f in h for f in frags):
            return cat
    low = text.lower()
    for cat, words in WORD_RULES:
        if any(w in low for w in words):
            return cat
    fpath = " ".join(folders).lower()
    if fpath:
        for cat, words in FOLDER_RULES:
            if any(w in fpath for w in words):
                return cat
    return "other"
