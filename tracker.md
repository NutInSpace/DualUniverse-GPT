-- OnTimer("scan")
```
local num_steps = 300
local name = ""
local last_name = ""

-- Forwards
for i = 1, num_steps do
    scans_completed = scans_completed + 1
    local current_id = last_id + i
    --system.print("Up:" .. current_id)
    name = DUSystem.getPlayerName(current_id)

    if name and #name > 1 then
        online_players = online_players + 1
        last_name = name
    end
end

-- Backwards
for i = 1, num_steps do
    scans_completed = scans_completed + 1
    local current_id = player_id - scans_completed/2 - i
    --system.print("Down:" .. current_id)
    name = DUSystem.getPlayerName(current_id)

    if name and #name > 1 then
        online_players = online_players + 1
        last_name = nam
    end
end

if online_players > max_online_players then
    max_online_players = online_players
end

 -- Update the screen text after both loops finish
screen.setCenteredText("Local Players: " .. max_online_players .. "\n\nLast Player: " .. last_name .. "\n\nScans Completed: " .. scans_completed)

    
-- Next Iteration
last_id = last_id + num_steps

-- Reset
if scans_completed > player_id then
    online_players = 1
    scans_completed = 0
end
```
-- onStart()
```
max_online_players = 1
online_players = 1
scans_completed = 0
player_id = DUPlayer.getId()
last_id = player_id

screen.setCenteredText("Scanning...\n\nWelcome "..DUSystem.getPlayerName(player_id))
unit.setTimer("scan", 0.1)
```

-- Link Setup 

1. Link program board to screen
2. rename slot to screen.
