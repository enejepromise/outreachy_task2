# Task 2 — Async URL Status Checker

**Outreachy Internship Contribution — Lusophone Technological Wishlist**  
Submitted by: PROMZYBA

---

## The Problem

Given a CSV file containing a list of URLs, the task is to:

- Read each URL from the file
- Send a request to check if it is reachable
- Print the HTTP status code for each URL in this format:
```
(STATUS_CODE)  URL
```

---

## The Real Challenge

In real-world systems, checking URLs involves more than just sending requests:

- Some URLs are malformed or incomplete
- Some servers do not respond properly to certain request types
- Checking URLs sequentially is too slow for large datasets
- Untrusted input from a CSV file can introduce security risks

---

## My Approach

This project goes beyond the basic requirement by building a **fast, reliable, and security-aware URL checker**.

### Core Philosophy
```
Validate → Secure → Check Concurrently → Present Clearly
```

---

## What Was Implemented

### 1. Asynchronous Processing *(Performance)*

Instead of checking URLs one by one, the tool uses `asyncio` and `httpx.AsyncClient` to check multiple URLs **at the same time**, significantly reducing total execution time on large datasets.

---

### 2. URL Cleaning & Normalization

Many URLs in real datasets are written without a scheme. The script automatically prepends `https://` where missing before any processing begins.
```
example.com  →  https://example.com
```

---

### 3. Input Validation

Only well-formed URLs are processed. Every URL must:

- Use the `http` or `https` scheme
- Contain a valid hostname

Invalid entries are safely skipped and flagged in the terminal output.

---

### 4. SSRF Protection *(Security)*

To reflect real-world security awareness, the script blocks any URL that resolves to an internal or private IP address, including:

- Private ranges — `192.168.x.x`, `10.x.x.x`
- Loopback — `127.0.0.1`
- Reserved/internal networks

This prevents the tool from unintentionally probing internal systems when processing untrusted input.

---

### 5. Controlled Concurrency

A semaphore limits the number of simultaneous requests to **20 at a time**. This prevents:

- Overloading external servers
- Network instability on the client side
- Unintentional abuse of third-party endpoints

---

### 6. HEAD → GET Fallback Strategy

Not all servers support `HEAD` requests. To maximise reliability:

1. The script first attempts a `HEAD` request *(lightweight — no body downloaded)*
2. If the server returns an error, it automatically retries with a full `GET` request

---

### 7. Error Handling

The script handles all common real-world failure scenarios without crashing:

| Error | Label Shown |
|---|---|
| Server took too long | `TIMEOUT` |
| Could not reach server | `CONNECTION_ERROR` |
| Redirect loop detected | `TOO_MANY_REDIRECTS` |
| Any other network issue | `REQUEST_ERROR(...)` |

---

### 8. Live Progress Feedback

As URLs are checked, the terminal displays real-time progress:
```
  [1/155] Checked: https://www.google.com
  [2/155] Checked: https://www.github.com
  ...
```

This improves transparency and confirms the tool is actively running.

---

### 9. Colour-Coded Output

Results are displayed with colour to make them immediately readable:
```
  (200)  https://www.google.com
  (404)  https://this-page-is-gone.com
  (TIMEOUT)  https://slow-server.com
```

| Colour | Meaning |
|---|---|
| 🟢 Green | Success — page is reachable |
| 🔴 Red | HTTP error — page exists but returned an error |
| 🟡 Yellow | Network issue — could not connect at all |

---

### 10. Sorted Results

The final output is organised for easy review:

- Successful responses appear first
- Errors and failures appear at the bottom

---

### 11. Summary & Execution Time

After all URLs are checked, a clear summary is printed:
```
───────────────────────────────────────────────────────
  Total URLs checked  :  155
  Reachable  (< 400)  :  120
  Unreachable / Error :  35
───────────────────────────────────────────────────────

  Finished in 104.74 seconds
```

---

## Project Structure
```
Outreachy_task2/
├── url_status_checker.py    # Main script
├── Task 2 - Intern.csv      # Input CSV file containing URLs
└── README.md                # Project documentation
```

---

## How to Run

### Step 1 — Install the dependency
```bash
pip install httpx
```

### Step 2 — Place the CSV file in the same folder as the script

Ensured the CSV has a column named exactly `urls`:
```csv
urls
https://www.google.com
https://www.github.com
```

### Step 3 — Run the script
```bash
python url_status_checker.py
```

Or pass a custom file name directly:
```bash
python url_status_checker.py "Task 2 - Intern.csv"
```



---

## Configuration

Key settings can be adjusted at the top of the script:

| Setting | Default | Description |
|---|---|---|
| `CSV_FILE_PATH` | `Task 2 - Intern.csv` | Default input file |
| `URL_COLUMN_NAME` | `urls` | CSV column containing the URLs |
| `REQUEST_TIMEOUT` | `10` | Seconds before a request times out |
| `MAX_CONCURRENT` | `20` | Maximum simultaneous requests |
| `FOLLOW_REDIRECTS` | `True` | Whether to follow 301/302 redirects |

---

## Key Takeaway

This project demonstrates not just the ability to complete the task, but to **think beyond it**:

- **Performance** — async execution for fast, concurrent URL checking
- **Reliability** — HEAD → GET fallback to handle non-standard servers
- **Security** — input validation and SSRF protection against untrusted data
- **Usability** — live progress, colour-coded output, and a clean summary

---

## Author

**PROMZYBA**  
Outreachy Internship Applicant — Cycle 32