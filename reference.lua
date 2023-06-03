-- Duplicate (requires link to core)
-- Purpose: Find every item on a core.
-- Args: Filter (Boolean) If only one exists then duplicate. This avoids duplicating the factory elements. Default True
-- Args: Maintain (integer) How many to make. If 0, then use element count on core.

function build_recipe_table(filter, maintain)
  recipes = {}

  if core == nil then
    system.print("Missing link to core!")
  else
    system.print("Duplicating:")
  end

  -- Find everything on the core
  core_items = {}
  for _, element in pairs(core.getElementIdList()) do
    item = core.getElementItemIdById(element)

    -- track how many we want to transfer
    core_items[item] = (core_items[item] or 0) + 1
  end

  -- Build Recipe List
  for item, qty in pairs(core_items) do
    if maintain ~= 0 then
      qty = maintain
    end
    if filter and qty == 1 then
      table.insert(recipes, { id = item, quantity = qty })
      system.print(getName(item) .. " -> " .. qty)
    end
  end

  return recipes
end

-- Cleanup (updates globals such as the blacklist)
-- Purpose: Runs an optimization to save memory
-- Args: None
local function cleanup()
  for i = #blacklist, 1, -1 do
    local blacklisted_item = blacklist[i].id

    -- Remove the blacklisted item from the recipes list
    for j = #chef, 1, -1 do
      if chef[j].id == blacklisted_item then
        table.remove(chef, j)
      end
    end

    -- Remove the blacklisted item from the blacklist itself and chef
    table.remove(blacklist, i)
  end
end

-- Reorder (updates globals such as the recipe list)
-- Purpose: Adds recipes back to memory, ordered by what we last cooked.
-- Args: None
-- Reorder cooked items
local function reorder()
  system.print("Reordering Chef!")
  -- Prioritize missing items and already cooked items
  local priorities = { uncooked, cooked }
  for _, priority in ipairs(priorities) do
    while #priority > 0 do
      table.insert(chef, priority[#priority])
      table.remove(priority)
    end
  end
end

-- setColor (link up to 10 lights to the program board)
-- Purpose: configure light R,G,B values.
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function setColor(red, green, blue)
    for _, light in ipairs(lights) do
        light.setColor(red, green, blue)
    end
end

-- setBlink (
-- setup: link up to 10 lights to the program board
-- Purpose: configure light R,G,B values
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function setBlink()
    for _, light in ipairs(lights) do
        light.setBlinkingTimeShift(0.25)
        light.setOffBlinkingDuration(2.5)
        light.setOnBlinkingDuration(0.50)
        light.setBlinkingState(true)
    end
end

-- setColorRand 
-- setup: link up to 10 lights to the program board
-- Purpose: configure light R,G,B values
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function setColorRand(red, green, blue)
    local randomLight = lights[math.random(#lights)]
    randomLight.setColor(red, green, blue)
end

-- redalertmode (example script)
-- setup: link up to 10 lights to the program board, onTimer("redalert")
-- Purpose: clears or configures light

local redalert_red = 3 --export: light red
local redalaert_green = 0 --export: light green
local redalert_blue = 0 --export: light blue

if not lights[1].isBlinking() then
    system.print("Setting lights")
    for _, light in ipairs(lights) do
        light.activate()
    end
    setColor(redalert_red, redalaert_green, redalert_blue)
    setBlink()
else
    system.print("Clearing lights")
    for _, light in ipairs(lights) do
        light.setBlinkingState(false)
        light.deactivate()
    end
end

-- Configuration is done
unit.exit()

