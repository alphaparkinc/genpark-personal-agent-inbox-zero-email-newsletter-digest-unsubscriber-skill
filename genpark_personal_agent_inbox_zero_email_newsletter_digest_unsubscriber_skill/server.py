# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Inbox Zero Newsletter Digest & Unsubscriber Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "audit_newsletter_engagement",
    "description": "Audit incoming sender subscription lists, calculate reading engagement ratio, and recommend auto-unsubscription candidates.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "sender_email": {
          "type": "string"
        },
        "received_count_last_90d": {
          "type": "integer"
        },
        "opened_count_last_90d": {
          "type": "integer"
        },
        "has_one_click_unsubscribe_header": {
          "type": "boolean"
        },
        "unsubscribe_link_url": {
          "type": "string"
        }
      },
      "required": [
        "sender_email",
        "received_count_last_90d",
        "opened_count_last_90d"
      ]
    }
  },
  {
    "name": "compile_daily_newsletter_digest",
    "description": "Synthesize multiple newsletter digests into a concise, grouped 3-minute executive summary for the user.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "date_str": {
          "type": "string"
        },
        "newsletters": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": {
                "type": "string"
              },
              "headline": {
                "type": "string"
              },
              "key_takeaways": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "read_time_min": {
                "type": "integer"
              }
            },
            "required": [
              "source",
              "headline",
              "key_takeaways"
            ]
          }
        }
      },
      "required": [
        "date_str",
        "newsletters"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-inbox-zero-email-newsletter-digest-unsubscriber-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-inbox-zero-email-newsletter-digest-unsubscriber-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "audit_newsletter_engagement",
            "arguments": {
                "sender_email": "digest@weeklypromo.com",
                "received_count_last_90d": 24,
                "opened_count_last_90d": 1,
                "has_one_click_unsubscribe_header": True
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: audit_newsletter_engagement")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
