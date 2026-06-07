import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import time
import os

def generate_solidot_digest():
    # 1. 抓取 Solidot 官方源
    solidot_rss = "https://www.solidot.org/index.rss"
    feed = feedparser.parse(solidot_rss)
    
    # 2. 计算 24 小时内的时间窗口
    now = datetime.now(timezone.utc)
    one_day_ago = now - timedelta(days=1)
    
    today_stories = []
    
    for entry in feed.entries:
        try:
            # 尝试解析 Solidot 的时间格式
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
            else:
                continue
        except Exception:
            continue
            
        if pub_time > one_day_ago:
            today_stories.append(entry)
            
    # 3. 如果当天有更新，合并为一条
    if today_stories:
        # 按照时间正序排列（从早到晚）
        today_stories.reverse()
        
        # 组装 HTML 摘要内容
        html_content = "<h3>今日 Solidot 资讯汇总：</h3><hr/><ul>"
        for idx, story in enumerate(today_stories, 1):
            summary_text = getattr(story, 'summary', '无摘要')
            html_content += f'''
            <li>
                <strong>{idx}. <a href="{story.link}" target="_blank">{story.title}</a></strong><br/>
                {summary_text}
            </li><br/>
            '''
        html_content += "</ul>"
        
        # 4. 生成新的 RSS XML
        fg = FeedGenerator()
        fg.id('my_solidot_daily_digest')
        fg.title('Solidot 每日精选日报')
        fg.link(href='https://raw.githubusercontent.com/' + os.environ.get('GITHUB_REPOSITORY', '') + '/main/solidot_daily.xml', rel='self')
        fg.description('将 Solidot 每天几十条资讯浓缩合并为一条')
        
        fe = fg.add_entry()
        fe.id(now.strftime("%Y-%m-%d"))
        fe.title(f"【Solidot 日报】{now.strftime('%Y年%m月%d日')} 资讯汇总")
        fe.content(html_content, type='html')
        fe.published(now)
        
        # 输出文件
        fg.rss_file('solidot_daily.xml')
        print(f"成功合并了 {len(today_stories)} 条资讯！")
    else:
        print("过去 24 小时内 Solidot 没有更新。")

if __name__ == "__main__":
    generate_solidot_digest()
