import feedparser
import webbrowser
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from datetime import datetime
import pytz

console = Console()

# Google News RSS Feed for latest business news
RSS_URL = "https://news.google.com/rss/search?q=business+latest&hl=en-IN&gl=IN&ceid=IN:en"

# Fetch news feed (disable cache for fresh news)
feed = feedparser.parse(RSS_URL, request_headers={"Cache-Control": "no-cache"})

# Convert GMT to IST
def gmt_to_ist(pub_date):
    gmt_time = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S GMT")  # Parse GMT time
    gmt_zone = pytz.timezone("GMT")
    ist_zone = pytz.timezone("Asia/Kolkata")
    local_time = gmt_zone.localize(gmt_time).astimezone(ist_zone)  # Convert to IST
    return local_time.strftime("%Y-%m-%d %I:%M %p")  # Format as IST

# Sort news by IST (latest first)
sorted_entries = sorted(feed.entries, key=lambda x: datetime.strptime(x.published, "%a, %d %b %Y %H:%M:%S GMT").astimezone(pytz.timezone("Asia/Kolkata")), reverse=True)

# Pagination Variables
page = 0
news_per_page = 10
total_news = len(sorted_entries)

def clear_console():
    """Clears the console to prevent glitching"""
    os.system("cls" if os.name == "nt" else "clear")

def show_news():
    """Display news in pages (10 per page)"""
    clear_console()
    table = Table(title=f"📰 Latest Business News ({page * news_per_page + 1} - {min((page + 1) * news_per_page, total_news)})", show_lines=True)
    
    table.add_column("No.", justify="center", style="cyan", width=5)
    table.add_column("Title", style="bold yellow", width=70)
    table.add_column("Published (IST)", justify="center", style="green", width=20)
    table.add_column("Source", justify="center", style="blue", width=15)

    links = {}

    start = page * news_per_page
    end = min((page + 1) * news_per_page, total_news)

    for idx in range(start, end):
        entry = sorted_entries[idx]
        news_no = idx + 1  # Global news number
        links[str(news_no)] = entry.link
        table.add_row(str(news_no), entry.title, gmt_to_ist(entry.published), entry.source.title)

    console.print(table)

    return links

while True:
    links = show_news()

    # User Interaction
    choice = Prompt.ask("\n📢 Enter news number to open, 'N' for next, 'P' for previous, 'Q' to quit", choices=[*links.keys(), "N", "P", "Q", "n", "p", "q"], default="N").upper()

    if choice == "Q":
        console.print("[bold red]🚪 Exiting...[/bold red]")
        break
    elif choice == "N":
        if (page + 1) * news_per_page < total_news:
            page += 1
        else:
            console.print("[bold yellow]⚠️ No more news available![/bold yellow]")
    elif choice == "P":
        if page > 0:
            page -= 1
        else:
            console.print("[bold yellow]⚠️ You're already on the first page![/bold yellow]")
    else:
        webbrowser.open(links[choice])
