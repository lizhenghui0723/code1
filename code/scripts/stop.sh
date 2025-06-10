#!/bin/bash
if [ -f ../scripts/backend.pid ]; then
  kill $(cat ../scripts/backend.pid) && rm ../scripts/backend.pid
  echo "后端已关闭。"
fi
if [ -f ../scripts/frontend.pid ]; then
  kill $(cat ../scripts/frontend.pid) && rm ../scripts/frontend.pid
  echo "前端已关闭。"
fi 