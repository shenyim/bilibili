#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"  # 进入脚本所在目录

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[run] $(date -u '+%F %T GMT') bilibili hot refresh"

$PYTHON_BIN bilibili_hot.py

# 只在有变化时提交，避免刷屏
git add bilibili.json || true
if ! git diff --cached --quiet; then
  git commit -m "chore: update bilibili hot $(date -u '+%F %T GMT')"
  git push origin main
else
  echo "[git] no changes"
fi

echo "[done] OK"
