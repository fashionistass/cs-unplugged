```scratch
when green flag clicked
ask [Please enter a decimal number between 0 and 31:] and wait
set [decimal number v] to (answer)
set [bit value v] to [32]
repeat until <(bit value) = [1]>
  set [bit value v] to ((bit value) / (2))
  if <<(decimal number) > (bit value)> or <(decimal number) = (bit value)>> then
    play note (72 v) for (0.5) beats
    set [decimal number v] to ((decimal number) - (bit value))
  else
    play note (48 v) for (0.5) beats
  end
end
```
