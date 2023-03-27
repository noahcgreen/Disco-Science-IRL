-- Send a regular pulse; used to ensure that the game is still running

local heartbeat_filename = 'disco-science-irl/heartbeat'

script.on_nth_tick(60, function (event)
    game.write_file(heartbeat_filename, "", nil, 1)
end)

-- Track currently researched ingredients

local ingredients_filename = "disco-science-irl/ingredients.txt"

local labs_active = false
local current_research = nil

function is_lab_active(lab)
    return lab.status == defines.entity_status.working or lab.status == defines.entity_status.low_power
end

function has_active_lab(force)
    for _, surface in pairs(game.surfaces) do
        local labs = surface.find_entities_filtered{force=force, type="lab"}
        for _, lab in ipairs(labs) do
            if is_lab_active(lab) then return true end
        end
    end

    return false
end

function get_research_ingredient_names(force)
    if force.current_research == nil then return {} end

    local names = ""
    for _, ingredient in ipairs(force.current_research.research_unit_ingredients) do
        names = names .. ingredient.name .. "\n"
    end
    return names
end

script.on_event(defines.events.on_tick, function (event)
    local force = game.forces["player"]

    local active = has_active_lab(force)
    local research = force.current_research
    
    if labs_active and not active then
        labs_active = false
        current_research = nil
        -- Labs are no longer active
        game.remove_path(ingredients_filename)
    elseif not labs_active and active then
        -- Labs became active
        labs_active = true
        current_research = research
        local ingredients = get_research_ingredient_names(force)
        game.write_file(ingredients_filename, ingredients, nil, 1)
    elseif active and research ~= current_research then
        -- Researched technology changed
        current_research = research
        local ingredients = get_research_ingredient_names(force)
        game.write_file(ingredients_filename, ingredients, nil, 1)
    end
end)
