# Task 2 — Async URL Status Checker

**Outreachy Internship Contribution — Lusophone Technological Wishlist**  
Submitted by: PROMZYBA
---

## The Problem
Given a CSV file containing a list of URLs, the task is to:

- Read each URL from the file  
- Send a request to check if it is reachable  
- Print the HTTP status code in this format:
(STATUS_CODE) URL

---

## The Real Challenge
In real-world systems, checking URLs involves more than just sending requests:

- Some URLs are malformed or incomplete  
- Some servers do not respond properly to certain request types  
- Sequential checking is slow for large datasets  
- Untrusted input (CSV) can introduce security risks  

---

## My Approach

This project goes beyond the basic requirement by building a **fast, reliable, and security-aware URL checker**.

### Core idea:
> Validate → Secure → Check concurrently → Present clearly

---

## What Was Implemented

### 1. Asynchronous Processing (Performance)

Instead of checking URLs one by one, this tool uses:

- `asyncio` + `httpx.AsyncClient`

This allows multiple URLs to be checked **at the same time**, significantly improving speed.

---

### 2. URL Cleaning & Normalization

Many URLs in real datasets are incomplete.
The script automatically fixes missing schemes before processing.

---

### 3. Input Validation

Only valid URLs are processed:
- Must include `http` or `https`
- Must contain a valid hostname

Invalid entries are safely skipped.

---

### 4. Security Enhancement (Custom Addition)

To stand out and reflect real-world awareness, additional security checks were implemented.

#### SSRF Protection Awareness

The script blocks URLs that resolve to:

- Private IP addresses (`192.168.x.x`)
- Loopback addresses (`127.0.0.1`)
- Reserved/internal networks  

This prevents the tool from unintentionally interacting with internal systems.

---
### 5. Controlled Concurrency
A semaphore limits the number of simultaneous requests.

This prevents:
- Overloading external servers  
- Network instability  
- Unintentional abuse of endpoints  

---

### 6. HEAD → GET Fallback Strategy

Some servers do not support `HEAD` requests.

To improve reliability:
- The script first attempts a `HEAD` request (faster)
- If it fails, it retries with `GET`
---
### 7. Error Handling

The script gracefully handles real-world failures:

- Timeout errors  
- Connection failures  
- Too many redirects  
- Unexpected request errors  
---
### 8. Live Progress Feedback

As URLs are being checked, the script displays
This improves usability and transparency.
---

### 9. Clean & Readable Output

Results are displayed in a structured and readable format:
(200)  https://www.espn.com.br/futebol/bola-de-prata/artigo/_/id/8242963/bola-de-prata-espnw-em-nome-do-avo-julia-bianchi-da-nova-cara-ao-futebol-feminino-e-fecha-temporada-como-a-melhor-do-brasil
(403)  https://www.sports-reference.com/olympics.html
(503)  http://www.espn.com.br/noticia/667127_aos-38-anos-volante-formiga-acerta-com-o-paris-saint-germain
(CONNECTION_ERROR) https://www.dailybreeze.com/sports/ci_12896074


- ✅ Green → Success  
- ❌ Red → HTTP error  
- ⚠️ Yellow → Network issue  

---

### 10. Result Sorting

Final output is organized for clarity:

- Successful responses first  
- Errors and failures after  

---

### 11. Summary & Execution Time

At the end, the script provides:
Total URLs checked  :  155
Reachable  (< 400)  :  120
Unreachable / Error :  35
───────────────────────────────────────────────────────
Finished in 104.74 seconds

## Project Structure
Outreachy_task2/
├── url_status_checker.py
├── Task 2 - Intern.csv
└── README.md

---
## How to Run

### 1. Install dependency
pip install httpx

---

### 2. Run the script
python check_url_status.py

---

## Key Takeaway

This project demonstrates not just the ability to complete the task, but to think beyond it:
- Performance (async execution)  
- Reliability (fallback strategies)  
- Security awareness (input validation + SSRF protection)  
- Usability (progress tracking + clean output)  
---

## Author
PROMZYBA
