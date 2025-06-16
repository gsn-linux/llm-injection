# llm-injection
LLM_prompt_injecton tool
# LLM Prompt Injection Tool

A simple tool for fuzzing parameters in raw HTTP requests and detecting potential bypasses in machine learning prompt injections.

## Features
- Supports HTTP `GET` and `POST` methods.
- Logs results in a JSONL format.
- Rate-limiting for requests.
- Easy to use with a wordlist for fuzzing.

## Usage
### Command-line options:
- `--url <URL>`: Target URL with `FUZZ` keyword in the URI or query.
- `--method`: HTTP method (`GET` or `POST`).
- `--param`: Parameter name to fuzz in the raw request body.
- `-r --raw-file`: Path to a raw request file (Burp style).
- `--rate-limit`: Rate limit (requests per second).
- `-w --wordlist`: Path to a wordlist file.
- `--log`: Log file path (default: `results.jsonl`).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
