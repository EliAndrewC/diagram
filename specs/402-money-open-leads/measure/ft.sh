#!/bin/bash
# usage: ft.sh pid bid keyword
curl -s -m 60 -A "Mozilla/5.0" -e "https://dl.ndl.go.jp/pid/$1/1/1" -X POST https://dl.ndl.go.jp/api/fulltext/search -H 'Content-Type: application/json' -d "{\"keyword\":\"$3\",\"keywords\":[\"$3\"],\"targets\":[{\"pid\":\"$1\",\"bids\":[\"$2\"]}],\"mode\":\"CONTENT\",\"sort\":\"CONTENT\",\"size\":10000,\"fullTextInterval\":false,\"ftInterval\":400}"
