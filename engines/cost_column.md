# Cost column

Recorded 2026-08-19. One first successful call. Numbers come from that run and from the public price page opened the same day.

## Receipt

```
openai | gpt-5.6-terra | 2357 | pong
```

engine: openai
model: gpt-5.6-terra
latency_ms: 2357
reply: pong

## Tokens

Captured from the live JSON `usage` object on the same path as `engines/hello_models.py`.

prompt_tokens: 13
completion_tokens: 4
total_tokens: 17
cached_tokens: 0

## Recorded price

Source: https://developers.openai.com/api/docs/pricing
Page opened: 2026-08-19
Row used: gpt-5.6-terra, standard short context
input: 2.00 USD per 1M tokens
output: 12.00 USD per 1M tokens

prompt USD: 13 * 2.00 / 1000000 = 0.000026
completion USD: 4 * 12.00 / 1000000 = 0.000048
recorded USD: 0.000074
