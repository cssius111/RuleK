#!/usr/bin/env bash
set -euo pipefail

# 清理缓存写入失败时生成的 .error 标记文件
find data/cache/api -name '*.error' -delete

