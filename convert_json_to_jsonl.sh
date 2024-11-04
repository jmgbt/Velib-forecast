#!/bin/bash
input_dir="./data"
output_dir="./output"

for file in "$input_dir"/*.json; do
  jq -c '.[]' "$file" > "$output_dir/${file##*/}.jsonl"
done
