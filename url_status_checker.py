"""
URL Status Checker
------------------
Reads a list of URLs from a CSV file and checks if each one is reachable.
All URLs are checked at the same time (concurrently) to save time.
 
Features:
- Cleans and validates URLs before checking them
- Blocks suspicious/internal IPs (SSRF protection)
- Shows live progress as each URL is checked
- Colors the output: green = OK, red = broken, yellow = error
- Sorts results so healthy URLs appear first
- Shows a summary and total time at the end
""" 
import asyncio       
import csv           
import sys           
import time        
import socket       
import ipaddress     
from pathlib import Path         
from urllib.parse import urlparse 
import httpx  
 
 
 
CSV_FILE_PATH    = Path("Task 2 - Intern.csv")   
URL_COLUMN_NAME  = "urls"                        
REQUEST_TIMEOUT  = 10                            
MAX_CONCURRENT   = 20                            
FOLLOW_REDIRECTS = True                          
 
# colour codes used to colour terminal output
 
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"   # turns off colour, back to default
 
 
# Clean & Validate URLs 
def normalize_url(raw_url: str) -> str:
    """Add https:// if the URL has no scheme."""
    if not raw_url.startswith(("http://", "https://")):
        return f"https://{raw_url}"
    return raw_url
 
 
def is_valid_url(url: str) -> bool:
    """Check that the URL has a valid scheme (http/https) and a host name."""
    parts = urlparse(url)
    return parts.scheme in ("http", "https") and bool(parts.netloc)
 
 
def is_safe_target(url: str) -> bool:
    """
    Block URLs that point to internal/private IPs.
    This prevents SSRF — where an attacker tricks the server into
    calling internal services like 192.168.x.x or 127.0.0.1.
    """
    try:
        hostname = urlparse(url).hostname          
        ip = socket.gethostbyname(hostname)       
        ip_obj = ipaddress.ip_address(ip)          
 
        # reject if the IP is private, loopback, or reserved
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
            return False
 
        return True
    except Exception:
        return False 
 
def sanitize_for_display(text: str) -> str:
    """Strip newlines from a URL so it can't mess up terminal output."""
    return text.replace("\n", "").replace("\r", "")
 
 
# Step 2: Load URLs from the CSV File 
def load_urls_from_csv(csv_path: Path) -> list[str]:
    """
    Open the CSV, read every URL, clean it, and return only the safe valid ones.
    Skipped URLs are printed so the user knows what was ignored and why.
    """
    valid_urls = []
 
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f) 
 
        for row in reader:
            raw = row[URL_COLUMN_NAME].strip()  # grab the URL, remove leading/trailing spaces
 
            if not raw:
                continue  
 
            url = normalize_url(raw)  # make sure it starts with http:// or https://
 
            if is_valid_url(url) and is_safe_target(url):
                valid_urls.append(url)        
            else:
                print(f"  [SKIPPED] {raw}")
 
    return valid_urls
 
 
#Step 3: Check Each URL (async) 
async def fetch_status(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> tuple[str, int | str]:
    """
    Send a request to a single URL and return its HTTP status code.
    """
    async with semaphore: 
        try:
            response = await client.head(url, follow_redirects=FOLLOW_REDIRECTS)
 
            if response.status_code >= 400:
                response = await client.get(url, follow_redirects=FOLLOW_REDIRECTS)
 
            return url, response.status_code  
 
        #Handles known failure modes 
        except httpx.TimeoutException:
            return url, "TIMEOUT"           
        except httpx.TooManyRedirects:
            return url, "TOO_MANY_REDIRECTS"  
 
        except httpx.ConnectError:
            return url, "CONNECTION_ERROR"  
 
        except httpx.RequestError as e:
            return url, f"REQUEST_ERROR({type(e).__name__})"  
 
 
async def check_all_urls(urls: list[str]) -> list[tuple[str, int | str]]:
    """
    Fire off all URL checks concurrently and collect results.
    Prints live progress so the user can see what's happening.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)  
 
    # Identify our checker to servers 
    headers = {"User-Agent": "URL-Checker/1.0"}
 
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers=headers) as client:
 
        # Create one async task per URL
        tasks = [fetch_status(client, url, semaphore) for url in urls]
 
        results = []
        total = len(tasks)
 
        # asyncio.as_completed() yields each task as soon as it finishes (not in order)
        for index, done_task in enumerate(asyncio.as_completed(tasks), start=1):
            result = await done_task
            results.append(result)
 
            # Show live progress:
            print(f"  [{index}/{total}] Checked: {sanitize_for_display(result[0])}")
 
    return results
 
 
#Step 4: Display Results
 
def colorize(status: int | str) -> str:
    """
    Wrap a status code in a colour:
    - Green  → success (anything below 400)
    - Red    → HTTP error (400 and above)
    - Yellow → network/connection error (string values like TIMEOUT)
    """
    if isinstance(status, int):
        color = GREEN if status < 400 else RED
    else:
        color = YELLOW  
    return f"{color}{status}{RESET}"
 
 
def print_result(url: str, status: int | str) -> None:
    """Print a single URL result with its coloured status code."""
    print(f"  ({colorize(status)})  {sanitize_for_display(url)}")
 
 
def print_summary(results: list[tuple[str, int | str]]) -> None:
    """Print a final tally: how many passed, how many failed."""
    total      = len(results)
    successful = sum(1 for _, s in results if isinstance(s, int) and s < 400)
    failed     = total - successful
 
    print("\n" + "─" * 55)
    print(f"  Total URLs checked  :  {total}")
    print(f"  Reachable  (< 400)  :  {successful}")
    print(f"  Unreachable / Error :  {failed}")
    print("─" * 55)
 
 
# Entry Point 
async def main() -> None:
    start = time.perf_counter()  
 
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_FILE_PATH
 
    # Make sure the file actually exists before we try to open it
    if not csv_path.exists():
        print(f"\n  Error: File not found → {csv_path}")
        sys.exit(1)
 
    print(f"\n  Loading URLs from: {csv_path}\n")
    urls = load_urls_from_csv(csv_path)
 
    if not urls:
        print("  No valid URLs to check. Exiting.")
        sys.exit(0)
 
    print(f"\n  Checking {len(urls)} URLs...\n")
    results = await check_all_urls(urls)
 
    # Sort so successful responses (int) come before errors (str)
    # Within each group, sort alphabetically by status code
    results.sort(key=lambda item: (isinstance(item[1], str), item[1]))
 
    print("\n  ── Results ──────────────────────────────────────────\n")
    for url, status in results:
        print_result(url, status)
 
    print_summary(results)
 
    elapsed = time.perf_counter() - start
    print(f"\n  Finished in {elapsed:.2f} seconds\n")
 
 
if __name__ == "__main__":
    asyncio.run(main())  