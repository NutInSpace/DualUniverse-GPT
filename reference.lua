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
local function reorder(maintain)
    system.print("Reordering Chef!")
    -- First Priority Missing Items
    if #uncooked > 0 then
        for _, item in ipairs(uncooked) do
            table.insert(chef, item)
        end
        uncooked = {}
    end

    -- Second Priority Already Cooked Items
    if #cooked > 0 then
        for _, item in ipairs(cooked) do
            table.insert(chef, item)
        end
        cooked = {}
    end
end

