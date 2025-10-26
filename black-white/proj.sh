for n in $(seq 649 -1 155); do
  old="image${n}.png"
  new=$((n - 1))
  new="image${new}.png"
  if [ -f "$old" ]; then
    mv "$old" "$new"
  fi
done
