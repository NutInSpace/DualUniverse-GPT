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

-- configureLights (link up to 10 lights to the program board)
-- Purpose: Configure light R,G,B values for all connected lights.
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function configureLights(red, green, blue)
    for _, light in ipairs(lights) do
        light.setColor(red, green, blue)
    end
end

-- setLightsBlink (link up to 10 lights to the program board)
-- Purpose: Configure light blinking settings for all connected lights.
function setLightsBlink()
    for _, light in ipairs(lights) do
        light.setBlinkingTimeShift(0.25)
        light.setOffBlinkingDuration(2.5)
        light.setOnBlinkingDuration(0.50)
        light.setBlinkingState(true)
    end
end

-- setRandomLightColor (link up to 10 lights to the program board)
-- Purpose: Configure light R,G,B values for a random connected light.
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function setRandomLightColor(red, green, blue)
    local randomLight = lights[math.random(#lights)]
    randomLight.setColor(red, green, blue)
end

local redAlertRed = 3 --export: light red
local redAlertGreen = 0 --export: light green
local redAlertBlue = 0 --export: light blue

if not lights[1].isBlinking() then
    system.print("Setting lights")
    for _, light in ipairs(lights) do
        light.activate()
    end
    configureLights(redAlertRed, redAlertGreen, redAlertBlue)
    setLightsBlink()
else
    system.print("Clearing lights")
    for _, light in ipairs(lights) do
        light.setBlinkingState(false)
        light.deactivate()
    end
end

-- Configuration is done
unit.exit()

-- Light Sequenceing Patterns (Advanced light configurations)
-- configureLights (link up to 10 lights to the program board)
-- Purpose: Configure light R,G,B values for all connected lights.
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function configureLights(red, green, blue)
    for _, light in ipairs(lights) do
        light.setColor(red, green, blue)
    end
end

-- setLightsBlink (link up to 10 lights to the program board)
-- Purpose: Configure light blinking settings for all connected lights.
function setLightsBlink()
    for _, light in ipairs(lights) do
        light.setBlinkingTimeShift(0.25)
        light.setOffBlinkingDuration(2.5)
        light.setOnBlinkingDuration(0.50)
        light.setBlinkingState(true)
    end
end

-- setRandomLightColor (link up to 10 lights to the program board)
-- Purpose: Configure light R,G,B values for a random connected light.
-- Args: red (integer) Min: 0, Max: 5
-- Args: green (integer) Min: 0, Max: 5
-- Args: blue (integer) Min: 0, Max: 5
function setRandomLightColor(red, green, blue)
    local randomLight = lights[math.random(#lights)]
    randomLight.setColor(red, green, blue)
end

-- sequenceLightPattern (link up to 10 lights to the program board)
-- Purpose: Sequence a pattern of colors for connected lights.
-- Args: pattern (table) - An array of color patterns, each containing red, green, and blue values.
-- Args: interval (number, optional) - The time interval between each color change. Default: 2.5 seconds.
function sequenceLightPattern(pattern, interval)
    interval = interval or 2.5 -- Set default interval value if not provided
    for i, color in ipairs(pattern) do
        for _, light in ipairs(lights) do
            light.setColor(color.red, color.green, color.blue)
        end
        os.sleep(interval)
    end
end

-- changeLightPattern
-- Purpose: Change the pattern of colors for sequencing the lights.
-- Args: newPattern (table) - An array of color patterns, each containing red, green, and blue values.
function changeLightPattern(newPattern)
    pattern = newPattern
end

-- addColorToPattern
-- Purpose: Add a new color pattern to the existing pattern for sequencing the lights.
-- Args: color (table) - A color pattern containing red, green, and blue values.
function addColorToPattern(color)
    table.insert(pattern, color)
end

-- Example colors
local red = { red = 5, green = 0, blue = 0 }     -- Red color
local green = { red = 0, green = 5, blue = 0 }   -- Green color
local blue = { red = 0, green = 0, blue = 5 }    -- Blue color
local yellow = { red = 5, green = 5, blue = 0 }  -- Yellow color
local purple = { red = 5, green = 0, blue = 5 }  -- Purple color
local cyan = { red = 0, green = 5, blue = 5 }    -- Cyan color

-- Define an initial pattern
local pattern = { red, green, blue }

-- Change the pattern
changeLightPattern(pattern)

-- Add new colors to the pattern
addColorToPattern(yellow)
addColorToPattern(purple)
addColorToPattern(cyan)

-- Use the updated pattern in the sequence with default interval
sequenceLightPattern(pattern)
