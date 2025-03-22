# these are saved curl requests, not an executable test.
#
curl -X POST "http://localhost:8000/v1/completions?lora=lora-a" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me something"}'

curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "X-LoRA-Module: lora-b" \
  -d '{"prompt": "Tell me something"}'

curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me something", "lora": "lora-a"}'

curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me something"}'

