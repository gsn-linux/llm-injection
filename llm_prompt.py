#!/usr/bin/env python3
import argparse
import time
import json
import requests
from urllib.parse import urlencode
from datetime import datetime

# --------- Bypass Detection ----------
def detect_bypass(response_data):
    text = json.dumps(response_data).lower()
    indicators = ["hacked", "access granted", "override", "bypassed"]
    return any(word in text for word in indicators)

# --------- Log to file ----------
def log_result(payload, response_data, bypassed, log_file):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
        "response": response_data,
        "bypass": bypassed
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# --------- Parse Raw Request ----------
def parse_raw_request(raw_file):
    with open(raw_file, "r") as f:
        raw = f.read()
    headers_part, body = raw.split("\n\n", 1)
    header_lines = headers_part.splitlines()
    method, path, _ = header_lines[0].split()
    headers = {}
    for line in header_lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    host = headers.get("Host", "")
    url = f"http://{host}{path}"
    return method, url, headers, body

# --------- Main Function ----------
def main():
    parser = argparse.ArgumentParser(description="LLM Prompt Injection Tool")
    parser.add_argument("--url", help="Target URL with FUZZ keyword in URI or query")
    parser.add_argument("--method", choices=["GET", "POST"], default="POST", help="HTTP method for --url mode")
    parser.add_argument("--param", help="Parameter name to fuzz in raw request body")
    parser.add_argument("-r", "--raw-file", help="Path to raw request file (Burp style)")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Rate limit (requests per second)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("--log", default="results.jsonl", help="Log file path")

    args = parser.parse_args()

    with open(args.wordlist, "r") as f:
        payloads = [line.strip() for line in f if line.strip()]

    rate_delay = 1 / args.rate_limit
    total = len(payloads)

    if args.raw_file:
        method, url, headers, body = parse_raw_request(args.raw_file)
        for i, payload in enumerate(payloads, 1):
            print(f"[{i}/{total}] Fuzzing payload: {payload}")
            mod_body = body.replace(f'"{args.param}": "FUZZ"', f'"{args.param}": "{payload}"')
            try:
                response = requests.request(method, url, headers=headers, data=mod_body)
                try:
                    data = response.json()
                except:
                    data = {"non_json": response.text}
                bypass = detect_bypass(data)
                log_result(payload, data, bypass, args.log)
                print(f"    → Bypass: {bypass}")
            except Exception as e:
                print(f"    → Error: {e}")
            time.sleep(rate_delay)
    elif args.url and "FUZZ" in args.url:
        for i, payload in enumerate(payloads, 1):
            print(f"[{i}/{total}] Fuzzing payload: {payload}")
            fuzzed_url = args.url.replace("FUZZ", payload)
            try:
                if args.method == "POST":
                    response = requests.post(fuzzed_url)
                else:
                    response = requests.get(fuzzed_url)
                try:
                    data = response.json()
                except:
                    data = {"non_json": response.text}
                bypass = detect_bypass(data)
                log_result(payload, data, bypass, args.log)
                print(f"    → Bypass: {bypass}")
            except Exception as e:
                print(f"    → Error: {e}")
            time.sleep(rate_delay)
    else:
        print("[!] Please provide either --url with FUZZ or -r with --param")

if __name__ == "__main__":
    main()
