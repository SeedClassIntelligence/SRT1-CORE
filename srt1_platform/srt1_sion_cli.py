"""
SRT-1 AUTO-GENERATED INTELLIGENCE
===================================
Architectural Roles: CLI_ENTRY_POINT
Key Symbols: main
"""
import json
import urllib.request
import urllib.error
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="SRT-1 SION Cryptographic Override Interface")
    parser.add_argument("--event-id", required=True, help="The ID of the enforcement event to override")
    parser.add_argument("--reason", required=True, help="Cryptographic approval reasoning for drift")
    parser.add_argument("--actor", default="cli_admin", help="Actor initiating the SION override")
    parser.add_argument("--endpoint", default="http://127.0.0.1:7483", help="SRT-1 instance endpoint")
    
    args = parser.parse_args()

    payload = json.dumps({
        "event_id": args.event_id,
        "reason": args.reason,
        "actor": args.actor
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url=f"{args.endpoint}/enforcement/override",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer cli_override_token"}
    )
    
    print(f"[!] Executing SION Override for event: {args.event_id}")
    try:
        with urllib.request.urlopen(req) as res:
            resp_body = res.read().decode("utf-8")
            data = json.loads(resp_body)
            print("[+] SION Override Successful!")
            print(json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print(f"[-] SION Override Failed: HTTP {e.code}")
        try:
            print(json.dumps(json.loads(e.read().decode("utf-8")), indent=2))
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
